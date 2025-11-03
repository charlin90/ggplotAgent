library(tidyverse)
library(ggrepel)

data <- read.csv("bio_complex_data.csv")

final_plot <- ggplot(data, aes(x = disease_stage, fill = drug_response)) +
  geom_bar(position = "fill") +
  scale_y_continuous(labels = scales::percent_format()) +
  labs(x = "Disease Stage", 
       y = "Percentage", 
       fill = "Drug Response",
       title = "Proportion of Responders and Non-responders by Disease Stage") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),
        plot.title = element_text(hjust = 0.5))

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)