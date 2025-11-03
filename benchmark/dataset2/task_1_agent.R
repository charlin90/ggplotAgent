library(tidyverse)
library(ggrepel)

# Read input data
data <- read.csv("__INPUT_FILE__")

# Create histogram plot
final_plot <- ggplot(data, aes(x = base_mean_expr)) +
  geom_histogram(
    bins = 30,
    fill = "steelblue",
    color = "white",
    alpha = 0.8
  ) +
  geom_vline(
    xintercept = mean(data$base_mean_expr),
    linetype = "dashed",
    color = "red",
    linewidth = 1
  ) +
  scale_x_log10() +
  theme_classic() +
  labs(
    title = "Distribution of Base Mean Expression",
    x = "Base Mean Expression (log10 scale)",
    y = "Frequency"
  )

# Save plots
ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)