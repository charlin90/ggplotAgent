import pyRserve
import os

class RInterface:
    def __init__(self, host='localhost', port=6311):
        try:
            self.conn = pyRserve.connect(host=host, port=port)
            print("Successfully connected to Rserve.")
        except pyRserve.errors.ConnectionRefusedError as e:
            print(f"Error: Connection to Rserve refused at {host}:{port}.")
            print("Please ensure Rserve is running in R: library(Rserve); Rserve(args='--no-save')")
            raise e
        except Exception as e:
            print(f"An unexpected error occurred during Rserve connection: {e}")
            raise e

    def generate_plot(self, plot_spec: dict, output_file_path: str = "plot.png") -> str:
        if not self.conn:
            raise ConnectionError("Not connected to Rserve. Please connect first.")

        try:
            # Ensure the directory for the output file exists
            output_dir = os.path.dirname(output_file_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"Created directory: {output_dir}")

            r_command_string = "library(ggplot2);\n"

            data_name = plot_spec.get('data', 'NULL')
            is_known_r_dataset = data_name in ['iris', 'mtcars'] # Add other known R datasets if needed

            if data_name == 'NULL' and not (plot_spec.get('x_variable') and plot_spec.get('y_variable')):
                 raise ValueError("Plot specification must include data source or explicit x/y variables for a dataless plot if supported.")


            if data_name != 'NULL':
                if is_known_r_dataset:
                    r_command_string += f"data({data_name});\n"
                # For file paths, R's working directory needs to be considered.
                # Assuming data files are accessible by Rserve's working directory or an absolute path.
                # For simplicity, if it's a path, we assume it's a CSV that R can load.
                # More robust handling would involve checking file type and using appropriate R load functions.
                elif isinstance(data_name, str) and (data_name.endswith(".csv") or data_name.endswith(".json")):
                    # Assuming R's working directory is /app where the script runs
                    # Or that data_name is an absolute path
                    # For CSVs, ensure correct loading. JSON would need a different loader.
                    if data_name.endswith(".csv"):
                         r_command_string += f"{data_name.split('.')[0]} <- read.csv('{data_name}');\n"
                         data_name = data_name.split('.')[0] # Use the dataframe name
                    else:
                        # Placeholder for other data types like JSON
                        print(f"Warning: Data loading for {data_name} type not fully implemented, assuming it's preloaded or R knows it.")


            # Base plot construction
            if plot_spec.get('x_variable') and plot_spec.get('y_variable'):
                aes_string = f"aes(x=`{plot_spec['x_variable']}`, y=`{plot_spec['y_variable']}`)"
                if data_name == 'NULL': # Plot without explicit dataframe, e.g. from calculated vectors
                    r_command_string += f"p <- ggplot(mapping={aes_string}) + "
                else:
                    r_command_string += f"p <- ggplot({data_name}, {aes_string}) + "
            elif plot_spec.get('x_variable'): # For plots like histograms that only need x
                aes_string = f"aes(x=`{plot_spec['x_variable']}`)"
                if data_name == 'NULL':
                     r_command_string += f"p <- ggplot(mapping={aes_string}) + "
                else:
                    r_command_string += f"p <- ggplot({data_name}, {aes_string}) + "
            else:
                raise ValueError("Plot specification must include at least x_variable for aes mapping.")

            plot_type = plot_spec.get('plot_type', 'geom_point') # Default to scatter if not specified
            r_command_string += f"{plot_type}();\n"

            # Add aesthetics like color
            color_var = plot_spec.get('color_variable')
            if color_var and data_name != 'NULL':
                # Using backticks for safety with column names that might have spaces or special chars
                r_command_string += f"p <- p + aes(color=factor(`{color_var}`));\n" # Corrected: removed extra parenthesis
                # The previous version had _ outside quote: factor({data_name}[['{color_var}']]))
                # R columns are accessed as data_frame$`column name` or data_frame[["column name"]]
                # For aes, it's simpler: aes(color = `column name`)
                # If data_name is part of the original plot_spec['data'] (e.g. 'iris'), then it's just aes(color=factor(Species))
                # If data_name was loaded from CSV, it's aes(color=factor(loaded_df_name$`Color Var`))
                # The current simplified approach assumes color_var is a direct column name in the data_name context.
                # A more robust way: aes(color = factor({data_name}$`{color_var}`)) or aes(color = factor(.data$`{color_var}`)) with dplyr

            # Add title
            title = plot_spec.get('title')
            if title:
                escaped_title = title.replace("'", "\\'")
                r_command_string += f"p <- p + labs(title='{escaped_title}');\n"

            # Add x-label
            x_label = plot_spec.get('x_label')
            if x_label:
                escaped_x_label = x_label.replace("'", "\\'")
                r_command_string += f"p <- p + labs(x='{escaped_x_label}');\n"

            # Add y-label
            y_label = plot_spec.get('y_label')
            if y_label:
                escaped_y_label = y_label.replace("'", "\\'")
                r_command_string += f"p <- p + labs(y='{escaped_y_label}');\n"

            # Save the plot
            # Ensure output_file_path is R-friendly (e.g. forward slashes)
            safe_output_file_path = output_file_path.replace("\\", "/")
            r_command_string += f"ggsave(filename='{safe_output_file_path}', plot=p);\n"

            print(f"\nExecuting R command:\n---\n{r_command_string}\n---")
            self.conn.eval(r_command_string)
            print(f"Plot successfully generated and saved to '{os.path.abspath(safe_output_file_path)}'")
            return os.path.abspath(safe_output_file_path)

        except pyRserve.rexceptions.PyRserveError as e: # Changed to PyRserveError
            print(f"Error during R execution: {e}")
            print(f"Failed R command was:\n{r_command_string}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred during plot generation: {e}")
            if 'r_command_string' in locals():
                 print(f"Potentially problematic R command was:\n{r_command_string}")
            raise

    def close(self):
        if self.conn:
            self.conn.close()
            print("Disconnected from Rserve.")

# Basic usage example
if __name__ == "__main__":
    print("Starting RInterface example...")
    r_interface = None
    try:
        r_interface = RInterface()

        # Example 1: Scatter plot from iris dataset
        scatter_spec = {
            "plot_type": "geom_point",
            "data": "iris",
            "x_variable": "Sepal.Length",
            "y_variable": "Petal.Width",
            "color_variable": "Species",
            "title": "Iris Flower Dimensions (Scatter)",
            "x_label": "Sepal Length (cm)",
            "y_label": "Petal Width (cm)"
        }
        print(f"\nGenerating plot with spec: {scatter_spec}")
        output_path_scatter = r_interface.generate_plot(scatter_spec, "test_scatter_plot.png")
        print(f"Scatter plot generated: {output_path_scatter}")

        # Example 2: Histogram from iris dataset
        histo_spec = {
            "plot_type": "geom_histogram",
            "data": "iris",
            "x_variable": "Sepal.Width",
            # "y_variable": Not needed for basic histogram
            "color_variable": "Species", # fill might be better for histogram
            "title": "Distribution of Sepal Width (Histogram)",
            "x_label": "Sepal Width (cm)",
            "y_label": "Frequency"
        }
        print(f"\nGenerating plot with spec: {histo_spec}")
        # Modify color mapping for histogram fill
        histo_spec_r_command = f"""
        library(ggplot2);
        data(iris);
        p <- ggplot(iris, aes(x=`{histo_spec['x_variable']}`)) +
             geom_histogram(aes(fill=factor(`{histo_spec['color_variable']}`)), alpha=0.7, position='identity') +
             labs(title='{histo_spec['title']}', x='{histo_spec['x_label']}', y='{histo_spec['y_label']}', fill='{histo_spec['color_variable']}');
        ggsave(filename='test_histogram_plot.png', plot=p);
        """
        print(f"\nExecuting custom R command for histogram:\n---\n{histo_spec_r_command}\n---")
        r_interface.conn.eval(histo_spec_r_command)
        output_path_histo = os.path.abspath("test_histogram_plot.png")
        print(f"Histogram plot generated: {output_path_histo}")


        # Example 3: Bar plot (conceptual - needs actual data or summarized data)
        # For a bar plot, ggplot typically expects x to be categorical and y to be counts/values,
        # or use geom_bar with stat="count" if y is not provided.
        # This example assumes pre-summarized data for simplicity if not using stat="count"

        # Create a dummy CSV for bar plot example
        dummy_data_content = "category,value\nA,10\nB,20\nC,15"
        dummy_csv_path = "dummy_bar_data.csv"
        with open(dummy_csv_path, "w") as f:
            f.write(dummy_data_content)
        print(f"\nCreated dummy CSV for bar plot: {dummy_csv_path}")

        bar_spec = {
            "plot_type": "geom_bar", # geom_col is often used for pre-summarized values
            "data": dummy_csv_path, # Path to CSV
            "x_variable": "category",
            "y_variable": "value", # y is specified, so geom_bar will use stat="identity" by default
            "color_variable": "category", # Color bars by category
            "title": "Sample Bar Plot from CSV",
            "x_label": "Category Type",
            "y_label": "Value Amount"
        }
        # For geom_bar with stat="identity" (the default when y is provided), fill is often better than color
        # Rewriting the R command for this specific bar plot case for clarity & better aesthetics

        # Load data from CSV first
        abs_dummy_csv_path = os.path.abspath(dummy_csv_path)
        r_interface.conn.eval(f"bar_data_df <- read.csv('{abs_dummy_csv_path}');")

        bar_spec_r_command = f"""
        library(ggplot2);
        p <- ggplot(bar_data_df, aes(x=`{bar_spec['x_variable']}`, y=`{bar_spec['y_variable']}`)) +
             geom_bar(stat="identity", aes(fill=factor(`{bar_spec['color_variable']}`))) +
             labs(title='{bar_spec['title']}', x='{bar_spec['x_label']}', y='{bar_spec['y_label']}', fill='{bar_spec['color_variable']}');
        ggsave(filename='test_bar_plot.png', plot=p);
        """
        print(f"\nExecuting custom R command for bar plot:\n---\n{bar_spec_r_command}\n---")
        r_interface.conn.eval(bar_spec_r_command)
        output_path_bar = os.path.abspath("test_bar_plot.png")
        print(f"Bar plot generated: {output_path_bar}")


    except pyRserve.rexceptions.PyRserveError as e: # Changed to PyRserveError
        print(f"RServe execution error in main: {e}")
    except pyRserve.errors.ConnectionRefusedError : # Explicitly catching this from constructor
        print("RServe connection refused in main. Ensure Rserve is running.")
    except Exception as e:
        print(f"An unexpected error occurred in main: {e}")
    finally:
        if r_interface:
            r_interface.close()
        # Clean up dummy CSV
        if os.path.exists("dummy_bar_data.csv"):
            os.remove("dummy_bar_data.csv")
            print("Cleaned up dummy_bar_data.csv")
        print("RInterface example finished.")
