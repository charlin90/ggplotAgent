library(tidyverse)
library(ggrepel)

your_data <- read.csv("__INPUT_FILE__")

final_plot <- ggplot(data = your_data, aes(x = biotype, fill = biotype)) +
  geom_bar() +
  geom_text(
    aes(label = after_stat(count)), 
    stat = "count", 
    vjust = -0.5, 
    size = 3
  ) +
  scale_fill_brewer(palette = "Set2") +
  scale_y_continuous(expand = expansion(mult = c(0, 0.1))) +
  theme_classic() +
  labs(
    title = "Count of Genes by Biotype",
    x = "Biotype",
    y = "Count",
    fill = "Biotype"
  )

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)