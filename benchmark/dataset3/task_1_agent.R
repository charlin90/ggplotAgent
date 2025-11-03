library(tidyverse)
library(ggrepel)

data <- read.csv("__INPUT_FILE__", check.names = FALSE)

processed_data <- data %>%
  mutate(
    log10_ic50 = log10(as.numeric(drug_sensitivity_ic50)),
    neg_log10_pvalue = -log10(as.numeric(p_value))
  )

final_plot <- ggplot(processed_data, aes(x = as.numeric(log2FoldChange), y = log10_ic50)) +
  geom_point(
    aes(
      color = chromosome,
      size = as.numeric(base_expression),
      shape = is_therapeutic_target
    ),
    alpha = 0.7
  ) +
  geom_hline(yintercept = mean(processed_data$log10_ic50), linetype = "dashed", color = "gray50") +
  geom_vline(xintercept = 0, linetype = "dashed", color = "gray50") +
  scale_color_viridis_d(option = "D") +
  scale_size_continuous(range = c(2, 6)) +
  scale_shape_manual(values = c(16, 17)) +
  labs(
    title = "Drug Sensitivity vs Gene Expression Fold Change",
    subtitle = "log10(IC50) vs log2FoldChange",
    x = "log2 Fold Change in Gene Expression",
    y = "log10(Drug Sensitivity IC50)",
    color = "Chromosome",
    size = "Base Expression",
    shape = "Therapeutic Target"
  ) +
  theme_classic(base_size = 12) +
  theme(
    legend.position = "right",
    plot.title = element_text(face = "bold"),
    panel.grid.minor = element_blank()
  )

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)