library(tidyverse)
library(ggrepel)

data <- read.csv("__INPUT_FILE__")

processed_data <- data %>%
  mutate(`Significance Group` = case_when(
    padj < 0.05 & log2FoldChange > 1 ~ "Upregulated",
    padj < 0.05 & log2FoldChange < -1 ~ "Downregulated",
    TRUE ~ "Not Significant"
  )) %>%
  mutate(`Significance Group` = factor(`Significance Group`,
                                      levels = c("Upregulated", "Downregulated", "Not Significant"))) %>%
  mutate(neg_log10_padj = -log10(padj))

final_plot <- ggplot(processed_data, aes(x = log2FoldChange, 
                          y = neg_log10_padj,
                          color = `Significance Group`)) +
  geom_point(alpha = 0.7, size = 2.5) +
  geom_vline(xintercept = c(-1, 1), linetype = "dashed", color = "gray50") +
  geom_hline(yintercept = -log10(0.05), linetype = "dashed", color = "gray50") +
  scale_color_manual(values = c("Upregulated" = "firebrick",
                               "Downregulated" = "dodgerblue",
                               "Not Significant" = "gray70")) +
  labs(x = "log2 Fold Change",
       y = "-log10(Adjusted p-value)",
       title = "Volcano Plot of Differential Expression",
       subtitle = "Colored by significance group",
       color = "Expression Status") +
  theme_classic() +
  theme(legend.position = "bottom",
        plot.title = element_text(face = "bold"),
        axis.text = element_text(size = 10),
        axis.title = element_text(size = 11))

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)