library(tidyverse)
library(ggrepel)

data <- read.csv("__INPUT_FILE__")

final_plot <- ggplot(data, aes(x = disease_stage, fill = drug_response)) +
  geom_bar(position = "fill") +
  geom_text_repel(
    aes(label = scales::percent(..count.. / sum(..count..))),
    stat = "count",
    position = position_fill(vjust = 0.5),
    size = 3.5,
    segment.size = 0.2,
    segment.color = "grey50"
  ) +
  scale_fill_manual(values = c("Responder" = "#2E8B57", "Non-responder" = "#DC143C")) +
  scale_y_continuous(labels = scales::percent) +
  labs(
    title = "Proportion of Drug Response by Disease Stage",
    subtitle = "Stacked bars show the percentage of responders and non-responders within each stage",
    x = "Disease Stage",
    y = "Proportion of Patients",
    fill = "Drug Response"
  ) +
  theme_classic()

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)