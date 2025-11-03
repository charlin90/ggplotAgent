library(tidyverse)
library(ggrepel)

data <- read.csv("synthetic_biodata_for_agent_test.csv")

data <- data %>%
  mutate(log10_ic50 = log10(drug_sensitivity_ic50))

final_plot <- ggplot(data, aes(x = log2FoldChange, y = log10_ic50)) +
  geom_point(alpha = 0.6, size = 2) +
  labs(x = "log2 Fold Change", y = "log10(IC50)") +
  theme_minimal() +
  theme(panel.grid.major = element_line(color = "gray90"),
        panel.grid.minor = element_blank(),
        panel.border = element_rect(color = "black", fill = NA, linewidth = 0.5))

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)