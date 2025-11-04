library(tidyverse)
library(ggrepel)

# Load the data
data <- read.csv("bio_complex_data.csv")

# Create the scatter plot
final_plot <- ggplot(data, aes(x = EGFR_expr, y = KRAS_expr, color = drug_response)) +
  geom_point(size = 3, alpha = 0.8) +
  labs(
    x = "EGFR Expression",
    y = "KRAS Expression",
    color = "Drug Response",
    title = "Relationship between EGFR and KRAS Expression by Drug Response"
  ) +
  theme_minimal()

# Save the plot in PNG and PDF formats
ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)