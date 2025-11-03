library(tidyverse)
library(ggrepel)

data <- read.csv("bio_data_master.csv")

final_plot <- ggplot(data, aes(x = biotype, y = log2FoldChange, fill = is_significant)) +
  geom_boxplot() +
  scale_fill_manual(values = c("Yes" = "red", "No" = "gray")) +
  labs(title = "Log2 Fold Change by Biotype",
       x = "Biotype",
       y = "Log2 Fold Change",
       fill = "Significant") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)