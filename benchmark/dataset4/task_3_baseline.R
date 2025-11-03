library(tidyverse)
library(ggrepel)

data <- read.csv("creative_viz_data.csv")

final_plot <- ggplot(data, aes(x = time_point, y = reorder(pathway, pathway_activity_score), fill = pathway_activity_score)) +
  geom_tile() +
  facet_grid(~ treatment, scales = "free", space = "free") +
  scale_fill_gradient2(low = "blue", mid = "white", high = "red", midpoint = median(data$pathway_activity_score)) +
  labs(x = "Time (hours)", y = "Pathway", fill = "Activity Score") +
  theme_minimal() +
  theme(axis.text.y = element_text(size = 6),
        axis.text.x = element_text(angle = 45, hjust = 1),
        strip.text = element_text(face = "bold"),
        panel.spacing = unit(0.5, "lines"))

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)