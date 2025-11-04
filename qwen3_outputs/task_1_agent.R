library(tidyverse)
library(ggrepel)

# Read the input data
data <- read.csv("__INPUT_FILE__")

# Create the final plot
final_plot <- ggplot(data, aes(x = disease_stage, y = EGFR_expr)) +
  geom_boxplot(aes(fill = disease_stage)) +
  geom_jitter(width = 0.2, alpha = 0.6) +
  scale_fill_viridis_d(option = "plasma") +
  theme_classic() +
  labs(
    title = "EGFR Expression Across Disease Stages",
    subtitle = "Box plot showing distribution of EGFR expression levels by clinical stage",
    x = "Disease Stage",
    y = "EGFR Expression Level",
    fill = "Disease Stage"
  )

# Save the plot in PNG and PDF formats
ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)