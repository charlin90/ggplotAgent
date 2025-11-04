library(tidyverse)
library(ggrepel)

# Load the data
data <- read.csv("bio_complex_data.csv")

# Create the age_group column
data <- data %>%
  mutate(age_group = ifelse(age < 50, "Young", "Old"))

# Create the violin plot for TP53 expression faceted by age group
final_plot <- ggplot(data, aes(x = age_group, y = TP53_expr, fill = age_group)) +
  geom_violin(trim = FALSE, alpha = 0.7) +
  facet_wrap(~ age_group, ncol = 2) +
  labs(
    title = "TP53 Expression by Age Group",
    x = "Age Group",
    y = "TP53 Expression Level"
  ) +
  theme_minimal() +
  theme(legend.position = "none")

# Save the plot in PNG and PDF formats
ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)