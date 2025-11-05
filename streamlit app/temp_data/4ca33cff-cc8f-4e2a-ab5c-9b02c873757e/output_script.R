library(tidyverse)
library(ggrepel)

# Read data
your_data <- read.csv("__INPUT_FILE__")

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
ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)