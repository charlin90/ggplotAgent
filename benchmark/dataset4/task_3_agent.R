library(tidyverse)
library(ggrepel)

# Read and preprocess data
data <- read.csv("__INPUT_FILE__")

processed_data <- data %>%
  mutate(
    time_point = as.numeric(time_point),
    time_factor = factor(time_point, levels = c(0, 24, 48, 72)),
    treatment = factor(treatment, levels = c("Control", "DrugX", "DrugZ"))
  ) %>%
  group_by(pathway, treatment, patient_id) %>%
  mutate(
    normalized_activity = scale(pathway_activity_score)
  ) %>%
  ungroup()

# Create heatmap visualization
final_plot <- ggplot(processed_data, 
                     aes(x = time_factor, 
                         y = reorder(pathway, normalized_activity), 
                         fill = normalized_activity)) +
  geom_tile(color = "white", linewidth = 0.2) +
  facet_grid(treatment ~ ., scales = "free_y", space = "free") +
  scale_fill_gradient2(
    low = "blue",
    mid = "white",
    high = "red",
    midpoint = 0,
    name = "Normalized\nPathway Activity"
  ) +
  theme_classic() +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1),
    strip.background = element_blank(),
    panel.spacing = unit(0.5, "lines")
  ) +
  labs(
    title = "Time-Series Pathway Activity Heatmap",
    subtitle = "Response to Control, DrugX, and DrugZ treatments over 72 hours",
    x = "Time Point (hours)",
    y = "Pathway",
    caption = "Normalized activity scores: blue = inhibited, red = activated"
  )

# Save plots
ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)