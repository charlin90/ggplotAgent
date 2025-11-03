library(tidyverse)
library(ggrepel)

data <- read.csv("__INPUT_FILE__")

final_plot <- ggplot(data, aes(x = gene_length)) +
  geom_density(fill = "steelblue", alpha = 0.6) +
  geom_rug(alpha = 0.3) +
  scale_x_log10() +
  theme_classic() +
  labs(title = "Gene Length Density Distribution",
       subtitle = "Distribution of gene lengths across all features",
       x = "Gene Length (bp)",
       y = "Density")

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)