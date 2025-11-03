library(tidyverse)
library(ggrepel)

data <- read.csv("bio_complex_data.csv")

final_plot <- data %>%
  arrange(desc(TP53_expr)) %>%
  mutate(patient_id = factor(patient_id, levels = patient_id)) %>%
  ggplot(aes(x = patient_id, y = TP53_expr, fill = drug_response)) +
  geom_bar(stat = "identity") +
  coord_polar(start = 0) +
  scale_fill_manual(values = c("Responder" = "blue", "Non-responder" = "orange")) +
  theme_minimal() +
  theme(
    axis.title = element_blank(),
    axis.text.y = element_blank(),
    panel.grid = element_blank(),
    axis.text.x = element_text(size = 8),
    legend.position = "bottom",
    plot.title = element_text(hjust = 0.5, size = 14, face = "bold")
  ) +
  labs(fill = "Drug Response")

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)