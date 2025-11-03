library(tidyverse)
library(ggrepel)

data <- read.csv("__INPUT_FILE__")

final_plot <- ggplot(data, aes(x = disease_stage, fill = drug_response)) +
  geom_bar(position = "fill") +
  scale_fill_manual(
    values = c("Responder" = "#1f78b4", "Non-responder" = "#e31a1c"),
    name = "Drug Response"
  ) +
  scale_y_continuous(labels = scales::percent) +
  theme_classic() +
  labs(
    title = "Proportion of Responders by Disease Stage",
    x = "Disease Stage",
    y = "Proportion of Patients"
  )

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)