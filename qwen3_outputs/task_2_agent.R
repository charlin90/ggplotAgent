library(tidyverse)
library(ggrepel)

# Read input data
data <- read.csv("__INPUT_FILE__")

# Preprocess data: filter responders, reshape to long format, clean gene names, and compute means
processed_data <- data %>%
  filter(drug_response == "Responder") %>%
  pivot_longer(cols = ends_with("_expr"), names_to = "gene", values_to = "expression") %>%
  mutate(gene = str_remove(gene, "_expr")) %>%
  group_by(gene) %>%
  summarise(expression = mean(expression), .groups = "drop")

# Create the final plot
final_plot <- ggplot(processed_data, aes(x = gene, y = expression)) +
  geom_col() +
  geom_text_repel(aes(label = round(expression, 2)), vjust = -0.5, segment.color = NA) +
  theme_classic() +
  labs(
    title = "Average Gene Expression in Responders",
    subtitle = "Mean expression levels across responder patients",
    x = "Gene",
    y = "Mean Expression",
    caption = "Data: Tumor gene expression profiles"
  )

# Save the plot in PNG and PDF formats
ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)