library(tidyverse)
library(ggrepel)

data <- read.csv("__INPUT_FILE__")

avg_expr <- data %>%
  filter(drug_response == "Responder") %>%
  pivot_longer(
    cols = ends_with("_expr"),
    names_to = "gene",
    values_to = "expression"
  ) %>%
  group_by(gene) %>%
  summarize(mean_expression = mean(expression, na.rm = TRUE))

final_plot <- ggplot(avg_expr, aes(x = gene, y = mean_expression, fill = gene)) +
  geom_col() +
  geom_text(aes(label = round(mean_expression, 2)), vjust = -0.5, size = 3.5) +
  scale_x_discrete(labels = function(x) gsub("_expr", "", x)) +
  scale_fill_brewer(palette = "Set1", guide = "none") +
  theme_classic() +
  labs(
    title = "Average Gene Expression in Responders",
    subtitle = "Mean expression values for each measured gene",
    x = "Gene",
    y = "Average Expression Level",
    caption = "Data from responder patients only"
  ) +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1),
    plot.title.position = "plot"
  )

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)