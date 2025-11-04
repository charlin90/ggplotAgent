library(tidyverse)
library(ggrepel)

# Read the data
data <- read.csv("bio_complex_data.csv")

# Filter for 'Responder' group and calculate average expression for each gene
avg_expr <- data %>%
  filter(drug_response == "Responder") %>%
  select(TP53_expr, EGFR_expr, KRAS_expr, BRCA1_expr) %>%
  summarise(across(everything(), mean, na.rm = TRUE)) %>%
  pivot_longer(everything(), names_to = "gene", values_to = "avg_expression")

# Create the bar chart
final_plot <- ggplot(avg_expr, aes(x = gene, y = avg_expression)) +
  geom_col(fill = "steelblue") +
  geom_text_repel(aes(label = round(avg_expression, 2)), vjust = -0.5) +
  labs(
    title = "Average Gene Expression in Responder Group",
    x = "Gene",
    y = "Average Expression"
  ) +
  theme_minimal()

# Save the plot in PNG and PDF formats
ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)