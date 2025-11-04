library(tidyverse)
library(ggrepel)

# Load the data
data <- read.csv("bio_complex_data.csv")

# Create the box plot for EGFR expression across disease stages
final_plot <- ggplot(data, aes(x = disease_stage, y = EGFR_expr)) +
  geom_boxplot(aes(fill = disease_stage)) +
  labs(
    title = "EGFR Expression Levels Across Disease Stages",
    x = "Disease Stage",
    y = "EGFR Expression Level"
  ) +
  theme_minimal() +
  theme(legend.position = "none")

# Save the plot in PNG and PDF formats
ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)