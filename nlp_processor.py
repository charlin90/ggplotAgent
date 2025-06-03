import spacy

class NLPProcessor:
    def __init__(self, model="en_core_web_sm"):
        try:
            self.nlp = spacy.load(model)
        except OSError:
            print(f"Spacy model '{model}' not found. Downloading and loading.")
            spacy.cli.download(model)
            self.nlp = spacy.load(model)

    def parse_description(self, description: str) -> dict:
        plot_info = {
            "plot_type": None,
            "data": None,
            "x_variable": None,
            "y_variable": None,
            "color_variable": None,
            "title": None,
            "x_label": None,
            "y_label": None,
        }
        doc = self.nlp(description)

        # Keyword mapping for plot types
        plot_type_keywords = {
            "scatter": "geom_point",
            "bar": "geom_bar",
            "histogram": "geom_histogram",
            "line": "geom_line",
        }

        # Plot type (ensure it's only set once and check lemma AND text)
        for token in doc:
            if not plot_info["plot_type"]:
                if token.lemma_ in plot_type_keywords:
                    plot_info["plot_type"] = plot_type_keywords[token.lemma_]
                elif token.text.lower() in plot_type_keywords: # check lowercased text too
                     plot_info["plot_type"] = plot_type_keywords[token.text.lower()]

        # Data Source Extraction (prioritize file names, then specific patterns)
        if not plot_info["data"]:
            for token in doc:
                if token.text.endswith((".csv", ".json", ".data", ".txt")):
                    plot_info["data"] = token.text
                    break # Found a file, likely the primary data source

        if not plot_info["data"]:
            for i, token in enumerate(doc):
                if token.lemma_ == "dataset" and i > 0 and doc[i-1].pos_ in ("NOUN", "PROPN"): # "iris dataset"
                    plot_info["data"] = doc[i-1].text
                    break
                if token.lemma_ in ("data", "dataset") and i + 1 < len(doc) and doc[i+1].lemma_ == "is" and i + 2 < len(doc) and doc[i+2].pos_ in ("NOUN", "PROPN"): # "data is iris"
                    plot_info["data"] = doc[i+2].text
                    break
                if token.lemma_ == "from" and i + 1 < len(doc) and doc[i+1].pos_ in ("NOUN", "PROPN"): # "from iris" / "from data.csv"
                    # Check if next token is dataset or already a file
                    if i + 2 < len(doc) and doc[i+2].lemma_ == "dataset":
                        plot_info["data"] = doc[i+1].text
                        break
                    elif doc[i+1].text.endswith((".csv", ".json", ".data", ".txt")):
                         plot_info["data"] = doc[i+1].text
                         break
                    elif not plot_info["data"] and doc[i+1].pos_ in ("NOUN", "PROPN"): # if not already a file, take it as a name
                        plot_info["data"] = doc[i+1].text # take "iris" from "from the iris dataset"
                        break
                if token.lemma_ == "using" and i + 1 < len(doc) and doc[i+1].pos_ in ("NOUN", "PROPN"):
                     plot_info["data"] = doc[i+1].text
                     break


        # Title, Labels, and Variables - iterating once with more specific pattern matching
        for i, token in enumerate(doc):
            current_lemma = token.lemma_
            current_text = token.text.lower()

            # Title
            if not plot_info["title"]:
                if current_lemma == "title":
                    if token.i + 1 < len(doc) and doc[token.i + 1].lemma_ == "be": # title is X
                        phrase = self._extract_phrase(doc, token.i + 2, support_multi_token=True)
                        if phrase: plot_info["title"] = phrase
                    elif token.i + 1 < len(doc) and doc[token.i+1].text == ":": # title: X
                        phrase = self._extract_phrase(doc, token.i + 2, support_multi_token=True)
                        if phrase: plot_info["title"] = phrase
                    # "titled 'X'" is handled by checking if current_text is "titled"
                elif current_text == "titled" and token.i + 1 < len(doc): # chart titled X
                    phrase = self._extract_phrase(doc, token.i + 1, support_multi_token=True)
                    if phrase: plot_info["title"] = phrase
                # "title should be X"
                elif current_lemma == "title" and token.i + 2 < len(doc) and doc[token.i+1].lemma_ == "should" and doc[token.i+2].lemma_ == "be":
                    phrase = self._extract_phrase(doc, token.i + 3, support_multi_token=True)
                    if phrase: plot_info["title"] = phrase


            # Labels
            for label_key, label_terms in [("x_label", ["xlabel", "x-label"]), ("y_label", ["ylabel", "y-label"])]:
                if not plot_info[label_key] and current_lemma in label_terms:
                    if token.i + 1 < len(doc) and (doc[token.i+1].text == ":" or doc[token.i+1].lemma_ == "be"):
                        phrase = self._extract_phrase(doc, token.i + 2, support_multi_token=True, allow_punct_in_phrase=True)
                        if phrase: plot_info[label_key] = phrase
                    elif token.i + 1 < len(doc) and doc[token.i+1].is_quote: # "x-label 'My Label'"
                         phrase = self._extract_phrase(doc, token.i + 1, support_multi_token=True, allow_punct_in_phrase=True)
                         if phrase: plot_info[label_key] = phrase
                    # "x-label Sales Region" (no colon, no quote)
                    elif token.i + 1 < len(doc):
                        phrase = self._extract_phrase(doc, token.i + 1, support_multi_token=True, allow_punct_in_phrase=True)
                        if phrase: plot_info[label_key] = phrase


            # Variables (X, Y, Color)
            # X-Variable
            if not plot_info["x_variable"]:
                if current_lemma in ("x-axis", "x_axis", "xvariable", "x-variable") or current_text == "x":
                    if i + 1 < len(doc) and (doc[i+1].lemma_ == "be" or doc[i+1].text == ":"):
                        # Handles "x-axis is 'Var'" or "x: Var"
                        phrase = self._extract_phrase(doc, i + 2, support_multi_token=False) # Variables are usually single tokens or dot-notation
                        if phrase: plot_info["x_variable"] = phrase
                    elif i + 2 < len(doc) and doc[i+1].lemma_ == "should" and doc[i+2].lemma_ == "be": # "x-axis should be Var"
                        phrase = self._extract_phrase(doc, i + 3, support_multi_token=False)
                        if phrase: plot_info["x_variable"] = phrase
                    elif i + 1 < len(doc) and doc[i+1].lemma_ == "as": # "x-axis as Age"
                        phrase = self._extract_phrase(doc, i+2, support_multi_token=False)
                        if phrase: plot_info["x_variable"] = phrase


                elif current_lemma == "use" and i + 3 < len(doc) and doc[i+2].lemma_ == "for" and doc[i+3].text.lower() == "x":
                    plot_info["x_variable"] = self._extract_quoted_or_text(doc[i+1]) # "Use Var for x"
                elif current_lemma == "plot" and i + 1 < len(doc) and doc[i+1].pos_ in ("NOUN", "PROPN", "SYM"):
                    var1 = self._extract_quoted_or_text(doc[i+1])
                    plot_info["x_variable"] = var1
                    if i + 3 < len(doc) and doc[i+2].lemma_ in ("vs", "versus", "against") and doc[i+3].pos_ in ("NOUN", "PROPN", "SYM"):
                        if not plot_info["y_variable"]:
                             var2 = self._extract_quoted_or_text(doc[i+3])
                             plot_info["y_variable"] = var2
                elif current_text == "of" and token.head.lemma_ in ("plot", "histogram", "chart") and i + 1 < len(doc) and doc[i+1].pos_ in ("NOUN", "PROPN", "SYM"):
                     if plot_info["plot_type"] == "geom_histogram": # Specifically for "histogram of X"
                        plot_info["x_variable"] = self._extract_quoted_or_text(doc[i+1])
                elif current_lemma == "variable" and i > 0 and doc[i-1].text.lower() == "x": # "X variable is Score"
                    if i + 1 < len(doc) and (doc[i+1].lemma_ == "be" or doc[i+1].text == ":") and i+2 < len(doc):
                        phrase = self._extract_phrase(doc, i+2, support_multi_token=False)
                        if phrase: plot_info["x_variable"] = phrase


            # Y-Variable
            if not plot_info["y_variable"]:
                if current_lemma in ("y-axis", "y_axis", "yvariable", "y-variable") or current_text == "y":
                    if i + 1 < len(doc) and (doc[i+1].lemma_ == "be" or doc[i+1].text == ":"):
                        phrase = self._extract_phrase(doc, i + 2, support_multi_token=False)
                        if phrase: plot_info["y_variable"] = phrase
                    elif i + 2 < len(doc) and doc[i+1].lemma_ == "should" and doc[i+2].lemma_ == "be":
                        phrase = self._extract_phrase(doc, i + 3, support_multi_token=False)
                        if phrase: plot_info["y_variable"] = phrase
                    elif i + 1 < len(doc) and doc[i+1].lemma_ == "as": # "y-axis as Income"
                        phrase = self._extract_phrase(doc, i+2, support_multi_token=False)
                        if phrase: plot_info["y_variable"] = phrase
                    elif i + 1 < len(doc) and token.head.lemma_ == "represents": # "y-axis representing 'Income'" (head is represents)
                         #This case is tricky, need to find object of representing
                         for child in token.head.children:
                             if child.dep_ == "dobj":
                                 plot_info["y_variable"] = self._extract_quoted_or_text(child)
                                 break


                elif current_lemma == "use" and i + 3 < len(doc) and doc[i+2].lemma_ == "for" and doc[i+3].text.lower() == "y":
                    plot_info["y_variable"] = self._extract_quoted_or_text(doc[i+1])
                elif current_lemma == "represents" and token.head.lemma_ in ("y-axis", "y_axis", "y") and i + 1 < len(doc): # "y-axis represents 'Var'" (token is represents)
                     phrase = self._extract_phrase(doc, i + 1, support_multi_token=False)
                     if phrase: plot_info["y_variable"] = phrase
                elif current_lemma == "variable" and i > 0 and doc[i-1].text.lower() == "y": # "Y variable is Total Sales"
                    if i + 1 < len(doc) and (doc[i+1].lemma_ == "be" or doc[i+1].text == ":") and i+2 < len(doc):
                        phrase = self._extract_phrase(doc, i+2, support_multi_token=False)
                        if phrase: plot_info["y_variable"] = phrase


            # Color Variable
            if not plot_info["color_variable"]:
                if current_lemma == "color" and i + 1 < len(doc) and doc[i+1].lemma_ == "by" and i + 2 < len(doc):
                    phrase = self._extract_phrase(doc, i + 2, support_multi_token=False)
                    if phrase: plot_info["color_variable"] = phrase
                elif current_text == "color" and i + 2 < len(doc) and doc[i+1].text == "by": # "color by X" (text match)
                    plot_info["color_variable"] = self._extract_quoted_or_text(doc[i+2])
                elif token.head.lemma_ == "by" and current_lemma == "color": # "colored by X"
                     # Search for the object of "by"
                    obj_of_by = None
                    for child in token.head.children:
                        if child.dep_ == "pobj":
                            obj_of_by = child
                            break
                    if obj_of_by:
                         plot_info["color_variable"] = self._extract_quoted_or_text(obj_of_by)


        # Fallback for data if specific patterns for variables didn't set it.
        # E.g. "scatter plot of X vs Y using iris"
        if not plot_info["data"]:
             for token in doc:
                 if token.lemma_ == "using" and token.i + 1 < len(doc) and doc[token.i+1].pos_ in ("NOUN", "PROPN") \
                    and doc[token.i+1].text not in [plot_info["x_variable"], plot_info["y_variable"], plot_info["color_variable"]]:
                     plot_info["data"] = doc[token.i+1].text
                     break


        # Clean up all extracted string values
        for key in plot_info:
            if plot_info[key] and isinstance(plot_info[key], str):
                plot_info[key] = plot_info[key].strip("'\" ")


        return plot_info

    def _extract_quoted_or_text(self, token) -> str:
        """Extracts text, preferring content within quotes if token itself is a quote."""
        if token.is_quote:
            # This case might be tricky if the token itself is the quote mark.
            # Usually, we'd look at the children or subsequent tokens.
            # For simplicity here, if it's a quote, we might need a broader context.
            # This helper is more for direct variable names that might be quoted.
            # Let's assume the token is the content itself for now if not quote.
            return token.text.strip("'\" ")
        # If the token has children and the first is a quote, implies a phrase like "'Sepal Length'"
        # This needs more robust handling in the main logic by looking ahead.
        return token.text.strip("'\" ")

    def _extract_phrase(self, doc, start_index, support_multi_token=False, allow_punct_in_phrase=False) -> str | None:
        """Extracts a phrase, potentially quoted or multi-token for labels/titles."""
        tokens_in_phrase = []
        if start_index >= len(doc):
            return None

        current_token = doc[start_index]

        if current_token.is_quote: # Starts with a quote "'Var Name'"
            # Move past the opening quote
            start_capture_index = start_index + 1
            for k in range(start_capture_index, len(doc)):
                if doc[k].is_quote: # Ending quote
                    break
                tokens_in_phrase.append(doc[k].text)
        elif support_multi_token: # For labels/titles that can be multi-word unquoted
            for k in range(start_index, len(doc)):
                # Include more POS tags that can be part of a label or title
                allowed_pos = ["NOUN", "PROPN", "ADJ", "NUM", "SYM", "PART", "CCONJ", "ADP"]
                if allow_punct_in_phrase: # for labels like "Sepal Length (cm)"
                    allowed_pos.append("PUNCT")

                if doc[k].pos_ in allowed_pos or (allow_punct_in_phrase and doc[k].text in "().-/:"):
                    tokens_in_phrase.append(doc[k].text)
                elif tokens_in_phrase: # Stop if we have something and encounter a non-phrase word
                    break
                else: # If nothing yet and not a valid start, stop.
                    break
        # For single variable names (potentially with dots, like 'Sepal.Length')
        # or single word after a keyword like "by Species"
        elif current_token.pos_ in ("NOUN", "PROPN", "SYM") or (current_token.pos_ == "X" and "." in current_token.text):
            # spaCy sometimes tags 'Sepal.Length' as X if it's out of context
            tokens_in_phrase.append(current_token.text)
            # Check if the next token is a dot and then another potential part of the variable name
            if start_index + 2 < len(doc) and doc[start_index+1].text == "." and doc[start_index+2].pos_ in ("NOUN", "PROPN", "SYM", "X"):
                tokens_in_phrase.append(".")
                tokens_in_phrase.append(doc[start_index+2].text)


        return " ".join(tokens_in_phrase).strip() if tokens_in_phrase else None

# Basic usage example
if __name__ == "__main__":
    processor = NLPProcessor()

    descriptions = [
        "Create a scatter plot of Sepal.Length vs Petal.Width from the iris dataset, color by Species. The title is 'Iris Flower Dimensions'. X-label: 'Sepal Length (cm)', y-label: 'Petal Width (cm)'.",
        "Generate a bar chart using sales_data.csv for sales across different regions. Title: 'Regional Sales Performance'. X-axis should be 'Region', Y-axis is 'Total Sales'. x-label 'Sales Region' and y-label 'Revenue (USD)'.",
        "Show a line plot of stock prices over time from stock_data. Use Date for x and Price for y. Color by Company. Title should be 'Stock Trends'.",
        "Plot a histogram of student scores. Data is student_grades.csv. X variable is 'Score'. Title: 'Distribution of Scores'. x-label: 'Scores Achieved'",
        "Make a scatter plot with x-axis as 'Age' and y-axis representing 'Income'. Use data 'census_data.json'. Title is 'Age vs Income'.",
        "Plot x_variable_name against y_variable_name, use data_source.csv, make it a line plot and title it 'My Simple Plot'. Color by category_column.",
        "x is 'col_A' and y is 'col_B', data: my.csv, type: scatter, title 'Test Plot'",
        "A bar chart titled 'Product Counts' with x-axis: Product and y-axis: Count from products.csv"
    ]

    for desc in descriptions:
        print(f"\nProcessing: {desc}")
        try:
            parsed_info = processor.parse_description(desc)
            print("Extracted Info:")
            for key, value in parsed_info.items():
                if value:  # Only print if a value was extracted
                    print(f"  {key}: {value}")
        except Exception as e:
            print(f"Error processing description: {e}")

    print("\n--- Testing specific extractions ---")
    test_scatter = "Make a scatter plot of 'Sepal Length' against 'Petal Width'."
    print(f"Input: {test_scatter}\nOutput: {processor.parse_description(test_scatter)}")

    test_labels = "Bar chart with x-label: 'Categories', y-label: 'Values'."
    print(f"Input: {test_labels}\nOutput: {processor.parse_description(test_labels)}")

    test_title = "Line plot. Title is 'My Awesome Data'."
    print(f"Input: {test_title}\nOutput: {processor.parse_description(test_title)}")

    test_data_source = "Histogram of values from 'my_data.csv'."
    print(f"Input: {test_data_source}\nOutput: {processor.parse_description(test_data_source)}")

    test_color = "Scatter plot of A vs B, color by C."
    print(f"Input: {test_color}\nOutput: {processor.parse_description(test_color)}")

    test_no_quotes = "scatter plot x-axis is acceleration y-axis is horsepower data is cars title is 'Speed Stats'"
    print(f"Input: {test_no_quotes}\nOutput: {processor.parse_description(test_no_quotes)}")
