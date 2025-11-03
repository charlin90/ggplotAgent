library(tidyverse)
library(ggrepel)

data <- read.csv("__INPUT_FILE__")

processed_data <- data %>%
  mutate(biotype = factor(biotype)) %>%
  mutate(neg_log10_pvalue = -log10(p_value))

final_plot <- ggplot(processed_data, aes(x = biotype, y = log2FoldChange)) +
  geom_boxplot(
    aes(fill = biotype),
    outlier.shape = NA,
    width = 0.6,
    alpha = 0.7
  ) +
  geom_jitter(
    width = 0.2,
    alpha = 0.5,
    size = 2,
    aes(color = is_significant)
  ) +
  geom_text_repel(
    data = . %>% filter(is_significant == "Yes"),
    aes(label = gene_symbol),
    size = 3,
    max.overlaps = 20,
    min.segment.length = 0.1,
    box.padding = 0.35,
    segment.color = "grey50"
  ) +
  scale_fill_viridis_d(option = "D", begin = 0.2, end = 0.8) +
  scale_color_manual(values = c("No" = "gray60", "Yes" = "red")) +
  theme_classic(base_size = 12) +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1),
    legend.position = "right",
    plot.title = element_text(face = "bold")
  ) +
  labs(
    title = "Distribution of log2FoldChange by Gene Biotype",
    subtitle = "Significant genes (padj < 0.05) labeled in red",
    x = "Gene Biotype",
    y = "log2 Fold Change",
    fill = "Biotype",
    color = "Significant"
  ) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "grey40")

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)