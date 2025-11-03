library(tidyverse)
library(ggrepel)

data <- read.csv("bio_data_master.csv")

final_plot <- ggplot(data, aes(x = gene_length, y = base_mean_expr, color = is_significant)) +
  geom_point(alpha = 0.7) +
  scale_color_manual(values = c("Yes" = "red", "No" = "gray50")) +
  labs(x = "Gene Length", y = "Base Mean Expression", color = "Significant") +
  theme_minimal() +
  theme(legend.position = "top")

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)