library(tidyverse)
library(ggrepel)

data <- read.csv("__INPUT_FILE__")

final_plot <- ggplot(data = data) +
  geom_boxplot(
    aes(x = biotype, y = log2FoldChange, fill = is_significant),
    outlier.shape = 21,
    alpha = 0.8
  ) +
  scale_fill_manual(
    values = c("Yes" = "firebrick", "No" = "steelblue"),
    name = "Significant"
  ) +
  theme_classic(base_size = 12) +
  labs(
    title = "Differential Expression by Gene Biotype",
    subtitle = "Boxplot of log2FoldChange values",
    x = "Gene Biotype",
    y = "log2(Fold Change)",
    caption = "Data from RNA-seq experiment"
  ) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)