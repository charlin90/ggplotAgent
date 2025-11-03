# Complete R script with fixes
library(tidyverse)
library(ggrepel)

data <- read.csv("__INPUT_FILE__")

processed_data <- data %>%
  arrange(desc(TP53_expr)) %>%
  mutate(
    patient_id = factor(patient_id, levels = patient_id),
    id = row_number(),
    angle = 90 - 360 * (id - 0.5) / nrow(.),
    hjust = ifelse(angle < -90, 1, 0),
    angle = ifelse(angle < -90, angle + 180, angle)
  )

final_plot <- ggplot(processed_data, aes(x = patient_id, y = TP53_expr, fill = drug_response)) +
  geom_bar(stat = "identity", width = 0.7) +  # Slightly narrower bars
  coord_polar(start = 0) +
  scale_fill_manual(
    values = c("Responder" = "blue", "Non-responder" = "orange"),
    name = "Drug Response"
  ) +
  scale_y_continuous(limits = c(0, max(processed_data$TP53_expr) * 1.1)) +
  geom_text_repel(
    aes(label = patient_id, y = TP53_expr + 1, angle = angle),  # Increased y-offset
    size = 2.5,  # Smaller text size
    box.padding = 0.3,  # Tighter padding
    point.padding = 0.2,
    segment.color = NA,
    show.legend = FALSE,
    max.overlaps = 20  # Allow more overlaps before removing labels
  ) +
  theme_minimal() +
  theme(
    axis.title = element_blank(),
    axis.text.y = element_blank(),
    axis.text.x = element_blank(),  # Remove patient_id from x-axis
    panel.grid.major.x = element_blank(),
    panel.grid.minor = element_blank(),
    legend.position = "bottom",
    plot.title = element_text(hjust = 0.5, face = "bold"),
    plot.margin = margin(1, 1, 1, 1, "cm")  # Add margin for labels
  ) +
  labs(
    title = "Patient TP53 Expression by Drug Response Status",
    subtitle = "Bars sorted by descending TP53 expression levels",
    fill = "Drug Response"
  )

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 10, height = 8, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 10, height = 8)