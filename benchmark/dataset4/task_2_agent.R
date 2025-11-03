library(tidyverse)
library(ggrepel)

data <- read.csv("__INPUT_FILE__")

plot_data <- data %>%
  filter(treatment == "DrugX", time_point == 72) %>%
  mutate(pathway = factor(pathway))

final_plot <- ggplot(plot_data, aes(x = pathway, y = pathway_activity_score)) +
  geom_violin(
    aes(fill = pathway),
    scale = "width",
    width = 0.7,
    trim = FALSE,
    draw_quantiles = 0.5,
    position = position_nudge(x = 0.2)
  ) +
  geom_boxplot(
    aes(color = pathway),
    width = 0.15,
    outlier.shape = NA,
    position = position_nudge(x = 0.2),
    show.legend = FALSE
  ) +
  geom_jitter(
    aes(color = pathway),
    width = 0.1,
    height = 0,
    alpha = 0.5,
    size = 2,
    show.legend = FALSE
  ) +
  scale_fill_viridis_d(option = "D", alpha = 0.6) +
  scale_color_viridis_d(option = "D") +
  labs(
    title = "Pathway Activity Scores for DrugX at 72 Hours",
    subtitle = "Rain cloud plot showing distribution by pathway",
    x = "Metabolic Pathway",
    y = "Pathway Activity Score",
    fill = "Pathway"
  ) +
  theme_classic() +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1),
    plot.title = element_text(face = "bold"),
    legend.position = "right"
  )

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)