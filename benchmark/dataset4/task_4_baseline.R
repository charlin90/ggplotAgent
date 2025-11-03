library(tidyverse)
library(ggridges)

data <- read.csv("creative_viz_data.csv")

final_plot <- ggplot(data, aes(x = pathway_activity_score, y = pathway, fill = pathway)) +
  geom_density_ridges(alpha = 0.7, scale = 0.9) +
  facet_wrap(~treatment, ncol = 1) +
  theme_minimal() +
  labs(x = "Pathway Activity Score", y = "Pathway") +
  theme(legend.position = "none",
        strip.text = element_text(size = 12, face = "bold"),
        axis.text.y = element_text(size = 10),
        axis.title = element_text(size = 12))

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)