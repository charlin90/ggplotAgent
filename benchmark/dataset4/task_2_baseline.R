library(tidyverse)
library(ggrepel)

data <- read.csv("creative_viz_data.csv")

filtered_data <- data %>%
  filter(treatment == "DrugX", time_point == 72)

final_plot <- ggplot(filtered_data, aes(x = pathway, y = pathway_activity_score)) +
  ggdist::stat_halfeye(
    aes(fill = pathway),
    adjust = 0.5,
    width = 0.6,
    .width = 0,
    justification = -0.2,
    point_colour = NA
  ) +
  geom_boxplot(
    aes(fill = pathway),
    width = 0.15,
    outlier.shape = NA,
    alpha = 0.5
  ) +
  geom_point(
    aes(color = pathway),
    position = position_jitter(width = 0.1, height = 0),
    size = 1.5,
    alpha = 0.6
  ) +
  labs(
    title = "Pathway Activity Scores at 72 Hours (DrugX Treatment)",
    x = "Pathway",
    y = "Activity Score"
  ) +
  theme_minimal() +
  theme(
    legend.position = "none",
    axis.text.x = element_text(angle = 45, hjust = 1),
    plot.title = element_text(hjust = 0.5)
  )

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)