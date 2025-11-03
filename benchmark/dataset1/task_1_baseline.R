library(tidyverse)
library(ggrepel)

data <- read.csv("bio_complex_data.csv")

final_plot <- ggplot(data, aes(x = disease_stage, y = EGFR_expr, fill = disease_stage)) +
  geom_boxplot(alpha = 0.8, outlier.shape = NA) +
  geom_jitter(width = 0.2, alpha = 0.5, size = 1.5) +
  labs(title = "EGFR Expression Across Disease Stages",
       x = "Disease Stage",
       y = "EGFR Expression Level") +
  theme_minimal() +
  theme(plot.title = element_text(hjust = 0.5, face = "bold"),
        axis.text = element_text(size = 10),
        axis.title = element_text(size = 12),
        legend.position = "none")

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)