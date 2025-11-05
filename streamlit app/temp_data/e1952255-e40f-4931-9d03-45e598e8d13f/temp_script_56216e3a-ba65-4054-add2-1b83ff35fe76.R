library(tidyverse)
library(ggrepel)

data <- read.csv("temp_data/e1952255-e40f-4931-9d03-45e598e8d13f/pie_example.csv")

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

ggsave("temp_data/e1952255-e40f-4931-9d03-45e598e8d13f/output_figure.png", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("temp_data/e1952255-e40f-4931-9d03-45e598e8d13f/output_figure.pdf", plot = final_plot, width = 8, height = 6)