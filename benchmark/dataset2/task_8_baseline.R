library(tidyverse)
library(ggrepel)

data <- read.csv("bio_data_master.csv")

final_plot <- ggplot(data, aes(x = base_mean_expr, y = log2FoldChange, color = biotype)) +
  geom_point(alpha = 0.7) +
  scale_x_log10() +
  scale_y_continuous(trans = scales::pseudo_log_trans(base = 10),
                     breaks = scales::extended_breaks(n = 7)) +
  theme_minimal() +
  theme(legend.position = "bottom") +
  labs(x = "Base Mean Expression (log10)", y = "Log2 Fold Change (symlog)")

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)