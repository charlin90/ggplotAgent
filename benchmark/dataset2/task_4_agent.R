library(tidyverse)
library(ggrepel)

# Read input data
data <- read.csv("__INPUT_FILE__")

# Create the plot
final_plot <- ggplot(data = data) +
  geom_point(aes(x = gene_length, y = base_mean_expr, color = is_significant), alpha = 0.6) +
  scale_color_manual(values = c("Yes" = "red", "No" = "gray60")) +
  scale_x_log10() +
  scale_y_log10() +
  annotation_logticks() +
  theme_classic() +
  labs(
    title = "Gene Expression vs. Gene Length",
    subtitle = "Points colored by differential expression significance",
    x = "Gene Length (bp)",
    y = "Mean Expression Level (base mean)",
    color = "Significant DE"
  )

# Save outputs
ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)