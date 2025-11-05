library(tidyverse)
library(ggrepel)

# Read data
your_data <- read.csv("temp_data/4ca33cff-cc8f-4e2a-ab5c-9b02c873757e/pie_example.csv")

# Create plot data with percentages
plot_data <- your_data %>%
  count(class) %>%
  mutate(percentage = n/sum(n))

# Create the plot
final_plot <- ggplot(plot_data, aes(x = "", y = percentage, fill = class)) +
  geom_bar(stat = "identity", width = 1, color = "white") +
  coord_polar("y", start = 0) +
  geom_text(
    aes(label = scales::percent(percentage)),
    position = position_stack(vjust = 0.5),
    color = "white"
  ) +
  scale_fill_brewer(palette = "Set2") +
  theme_void() +
  labs(
    title = "Distribution of Classes",
    fill = "Class"
  )

# Save plots
ggsave("temp_data/4ca33cff-cc8f-4e2a-ab5c-9b02c873757e/output_figure.png", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("temp_data/4ca33cff-cc8f-4e2a-ab5c-9b02c873757e/output_figure.pdf", plot = final_plot, width = 8, height = 6)