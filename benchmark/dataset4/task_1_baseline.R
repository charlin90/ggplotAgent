library(tidyverse)
library(ggrepel)

data <- read.csv("creative_viz_data.csv")

apoptosis_data <- data %>%
  filter(pathway == "Apoptosis") %>%
  group_by(treatment, time_point) %>%
  summarize(
    mean_score = mean(pathway_activity_score),
    sd_score = sd(pathway_activity_score)
  )

final_plot <- ggplot(apoptosis_data, aes(x = time_point, y = mean_score, color = treatment)) +
  geom_point(size = 3) +
  geom_errorbar(aes(ymin = mean_score - sd_score, ymax = mean_score + sd_score), width = 2) +
  geom_line(aes(group = treatment)) +
  facet_wrap(~treatment) +
  labs(
    x = "Time Point",
    y = "Mean Pathway Activity Score",
    title = "Apoptosis Pathway Activity by Treatment",
    color = "Treatment"
  ) +
  theme_minimal() +
  theme(
    legend.position = "none",
    plot.title = element_text(hjust = 0.5, face = "bold")
  )

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)