library(tidyverse)
library(ggrepel)

# Read input data
data <- read.csv("__INPUT_FILE__")

# Preprocess data: select relevant columns and pivot to long format
data_long <- data %>%
  select(drug_response, BRCA1_expr, TP53_expr) %>%
  pivot_longer(
    cols = c(BRCA1_expr, TP53_expr),
    names_to = "gene",
    names_pattern = "(.*)_expr",
    values_to = "expression"
  )

# Create the final plot
final_plot <- ggplot(data_long, aes(x = drug_response, y = expression, fill = drug_response)) +
  geom_boxplot() +
  facet_wrap(~ gene) +
  labs(
    title = "BRCA1 and TP53 Expression by Treatment Response",
    x = "Drug Response",
    y = "Gene Expression",
    fill = "Response Group"
  ) +
  theme_classic()

# Save the plot in PNG and PDF formats
ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)