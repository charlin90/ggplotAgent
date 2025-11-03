library(tidyverse)
library(ggrepel)

data <- read.csv("__INPUT_FILE__")

apoptosis_data <- data %>% 
  filter(pathway == "Apoptosis")

summary_data <- apoptosis_data %>%
  group_by(treatment, time_point) %>%
  summarise(
    mean_score = mean(pathway_activity_score, na.rm = TRUE),
    sd_score = sd(pathway_activity_score, na.rm = TRUE)
  ) %>%
  ungroup()

final_plot <- ggplot(summary_data, aes(x = time_point, y = mean_score, 
                        color = treatment, group = treatment)) +
  geom_line() +
  geom_point(size = 3) +
  geom_errorbar(aes(ymin = mean_score - sd_score, 
                    ymax = mean_score + sd_score), 
                width = 2) +
  facet_wrap(~ treatment) +
  theme_classic() +
  labs(title = "Apoptosis Pathway Activity Over Time",
       subtitle = "Mean activity score with standard deviation",
       x = "Time Point",
       y = "Mean Pathway Activity Score",
       color = "Treatment")

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)