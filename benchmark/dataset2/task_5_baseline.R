library(tidyverse)
library(ggrepel)

data <- read.csv("bio_data_master.csv")

final_plot <- ggplot(data, aes(x = biotype, y = log2FoldChange)) +
  geom_boxplot(outlier.shape = NA) +
  geom_jitter(width = 0.2, alpha = 0.5, aes(color = is_significant)) +
  scale_color_manual(values = c("No" = "gray50", "Yes" = "red")) +
  labs(title = "Log2 Fold Change by Biotype",
       x = "Biotype",
       y = "Log2 Fold Change",
       color = "Significant") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)