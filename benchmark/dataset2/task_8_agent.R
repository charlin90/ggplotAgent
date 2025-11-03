library(tidyverse)
library(ggrepel)

your_data <- read.csv("__INPUT_FILE__")

final_plot <- ggplot(data = your_data, aes(x = base_mean_expr, y = log2FoldChange, color = biotype)) +
  geom_point(alpha = 0.7) +
  scale_x_log10() +
  scale_y_continuous(trans = scales::pseudo_log_trans(base = 2)) +
  scale_color_brewer(palette = "Set1") +
  theme_minimal() +
  theme(legend.position = "bottom") +
  labs(
    title = "Differential Expression Analysis",
    subtitle = "Log2FoldChange vs. Base Mean Expression",
    x = "Base Mean Expression (log10)",
    y = "Log2 Fold Change (symlog)",
    color = "Gene Biotype"
  )

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)