library(tidyverse)
library(ggrepel)

data <- read.csv("__INPUT_FILE__")

processed_data <- data %>%
  mutate(age_group = if_else(age < 50, "Young", "Old")) %>%
  select(patient_id, age_group, TP53_expr)

final_plot <- ggplot(processed_data, aes(x = age_group, y = TP53_expr)) +
  geom_violin(aes(fill = age_group), width = 0.8, alpha = 0.7) +
  geom_jitter(width = 0.1, size = 2, alpha = 0.5) +
  stat_summary(fun = median, geom = "crossbar", width = 0.2, color = "black") +
  scale_fill_manual(values = c("Young" = "#66c2a5", "Old" = "#fc8d62")) +
  labs(title = "TP53 Expression by Age Group",
       subtitle = "Violin plot showing distribution of TP53 expression levels",
       x = "Age Group",
       y = "TP53 Expression Level",
       fill = "Age Group") +
  theme_classic() +
  theme(plot.title = element_text(face = "bold", size = 14),
        axis.title = element_text(size = 12),
        legend.position = "right")

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)