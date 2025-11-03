library(tidyverse)
library(ggrepel)

data <- read.csv("__INPUT_FILE__")

final_plot <- ggplot(data, aes(x = pathway_activity_score, fill = pathway)) +
  geom_density(alpha = 0.7) +
  facet_grid(pathway ~ treatment, scales = "free_y") +
  scale_fill_viridis_d(option = "magma") +
  scale_x_continuous(expand = c(0, 0)) +
  theme_classic() +
  theme(
    strip.background = element_rect(fill = "grey95"),
    axis.text.y = element_blank(),
    axis.ticks.y = element_blank(),
    panel.spacing = unit(0.1, "lines")
  ) +
  labs(
    title = "Pathway Activity Score Distributions",
    subtitle = "Faceted by Treatment Group",
    x = "Pathway Activity Score",
    y = "Density",
    fill = "Pathway"
  )

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)