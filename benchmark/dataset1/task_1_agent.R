library(tidyverse)
library(ggrepel)

# Read data
data <- read.csv("__INPUT_FILE__")

# Create plot
final_plot <- ggplot(data, aes(x = disease_stage, y = EGFR_expr)) +
  geom_boxplot(aes(fill = disease_stage), 
               width = 0.6,
               outlier.shape = NA) +
  geom_jitter(width = 0.2, 
              alpha = 0.5,
              size = 2,
              aes(color = disease_stage)) +
  scale_fill_viridis_d(option = "D", alpha = 0.7) +
  scale_color_viridis_d(option = "D") +
  labs(title = "EGFR Expression Across Disease Stages",
       subtitle = "Comparison of expression levels by pathological stage",
       x = "Disease Stage",
       y = "EGFR Expression Level",
       fill = "Disease Stage",
       color = "Disease Stage") +
  theme_classic(base_size = 14) +
  theme(plot.title = element_text(face = "bold"),
        legend.position = "right",
        axis.text.x = element_text(angle = 45, hjust = 1))

# Save plots
ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)