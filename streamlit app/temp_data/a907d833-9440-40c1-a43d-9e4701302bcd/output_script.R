library(tidyverse)
library(ggrepel)

your_data <- read.csv("__INPUT_FILE__")

final_plot <- ggplot(your_data, aes(x = "", fill = class)) +
  geom_bar(width = 1) +
  stat_count(geom = "text", aes(label = after_stat(count)), 
             position = position_stack(vjust = 0.5)) +
  coord_polar("y") +
  scale_fill_brewer(palette = "Set1") +
  scale_y_continuous(breaks = NULL) +
  theme_void() +
  labs(title = "Distribution of Classes", fill = "Class")

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)