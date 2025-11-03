library(tidyverse)
library(ggrepel)

data <- read.csv("bio_complex_data.csv")

plot_data <- data %>%
  select(patient_id, drug_response, TP53_expr, BRCA1_expr) %>%
  pivot_longer(cols = c(TP53_expr, BRCA1_expr), 
               names_to = "gene", 
               values_to = "expression") %>%
  mutate(gene = str_remove(gene, "_expr"))

final_plot <- ggplot(plot_data, aes(x = drug_response, y = expression, fill = drug_response)) +
  geom_boxplot() +
  facet_wrap(~gene) +
  theme_classic() +
  labs(x = "Drug Response", y = "Expression Level", fill = "Drug Response")

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)