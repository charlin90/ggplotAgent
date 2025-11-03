library(tidyverse)
library(ggrepel)

data <- read.csv("bio_complex_data.csv")

responder_data <- data %>%
  filter(drug_response == "Responder") %>%
  select(ends_with("_expr")) %>%
  summarise(across(everything(), mean, na.rm = TRUE)) %>%
  pivot_longer(everything(), names_to = "gene", values_to = "mean_expression") %>%
  mutate(gene = str_remove(gene, "_expr"))

final_plot <- ggplot(responder_data, aes(x = reorder(gene, -mean_expression), y = mean_expression)) +
  geom_bar(stat = "identity", fill = "steelblue") +
  labs(title = "Average Gene Expression in Responders",
       x = "Gene",
       y = "Mean Expression Level") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)