library(tidyverse)
library(ggrepel)

data <- read.csv("__INPUT_FILE__")

# Pre-calculate counts and percentages
plot_data <- data %>%
  count(class) %>%
  mutate(percentage = n/sum(n))

final_plot <- plot_data %>% 
  ggplot(aes(x = "", y = n, fill = class)) +
  geom_bar(stat = "identity", width = 1, color = "white") +
  coord_polar(theta = "y") +
  ggrepel::geom_text_repel(
    aes(label = scales::percent(percentage)),
    position = position_stack(vjust = 0.5),
    show.legend = FALSE
  ) +
  scale_fill_brewer(palette = "Set1") +
  theme_void() +
  labs(
    title = "Distribution of Classes",
    fill = "Class"
  )

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)