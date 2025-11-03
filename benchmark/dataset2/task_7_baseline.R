library(tidyverse)
library(ggrepel)

data <- read.csv("bio_data_master.csv")

data <- data %>%
  mutate(`Significance Group` = case_when(
    padj < 0.05 & log2FoldChange > 1 ~ "Upregulated",
    padj < 0.05 & log2FoldChange < -1 ~ "Downregulated",
    TRUE ~ "Not Significant"
  )) %>%
  mutate(`Significance Group` = factor(`Significance Group`, 
                                      levels = c("Upregulated", "Downregulated", "Not Significant")))

final_plot <- ggplot(data, aes(x = log2FoldChange, y = -log10(padj), color = `Significance Group`)) +
  geom_point(alpha = 0.7, size = 2) +
  scale_color_manual(values = c("Upregulated" = "red", "Downregulated" = "blue", "Not Significant" = "gray")) +
  geom_hline(yintercept = -log10(0.05), linetype = "dashed", color = "black") +
  geom_vline(xintercept = c(-1, 1), linetype = "dashed", color = "black") +
  labs(x = "log2 Fold Change", y = "-log10(Adjusted p-value)", 
       title = "Volcano Plot of Differential Expression") +
  theme_minimal() +
  theme(legend.position = "right")

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)