library(tidyverse)
library(ggrepel)

your_data <- read.csv("temp_data/a907d833-9440-40c1-a43d-9e4701302bcd/pie_example.csv")

final_plot <- ggplot(your_data, aes(x = "", fill = class)) +
  geom_bar(width = 1) +
  stat_count(geom = "text", aes(label = after_stat(count)), 
             position = position_stack(vjust = 0.5)) +
  coord_polar("y") +
  scale_fill_brewer(palette = "Set1") +
  scale_y_continuous(breaks = NULL) +
  theme_void() +
  labs(title = "Distribution of Classes", fill = "Class")

ggsave("temp_data/a907d833-9440-40c1-a43d-9e4701302bcd/output_figure.png", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("temp_data/a907d833-9440-40c1-a43d-9e4701302bcd/output_figure.pdf", plot = final_plot, width = 8, height = 6)