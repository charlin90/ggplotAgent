library(tidyverse)
library(ggrepel)

data <- read.csv("bio_complex_data.csv")

data <- data %>%
  mutate(age_group = ifelse(age < 50, "Young", "Old"))

final_plot <- ggplot(data, aes(x = age_group, y = TP53_expr, fill = age_group)) +
  geom_violin(trim = FALSE) +
  facet_wrap(~age_group, scales = "free") +
  labs(title = "TP53 Expression by Age Group",
       x = "Age Group",
       y = "TP53 Expression Level") +
  theme_minimal() +
  theme(legend.position = "none")

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)