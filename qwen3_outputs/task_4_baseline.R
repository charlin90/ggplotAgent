library(tidyverse)
library(ggrepel)

# Load the data
data <- read.csv("bio_complex_data.csv")

# Create the stacked bar chart showing proportions of Responders and Non-responders by disease stage
final_plot <- data %>%
  count(disease_stage, drug_response) %>%
  group_by(disease_stage) %>%
  mutate(proportion = n / sum(n)) %>%
  ggplot(aes(x = disease_stage, y = proportion, fill = drug_response)) +
  geom_col() +
  scale_y_continuous(labels = scales::percent_format()) +
  labs(
    x = "Disease Stage",
    y = "Proportion",
    fill = "Drug Response"
  ) +
  theme_minimal()

# Save the plot in PNG and PDF formats
ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)