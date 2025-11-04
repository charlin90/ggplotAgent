library(tidyverse)
library(ggrepel)

data <- read.csv("__INPUT_FILE__")

data <- data %>%
  mutate(age_group = if_else(age < 50, "Young", "Old"))

final_plot <- ggplot(data, aes(x = age_group, y = TP53_expr, fill = age_group)) +
  geom_violin(trim = FALSE) +
  scale_fill_manual(values = c("Young" = "#66C2A5", "Old" = "#FC8D62")) +
  labs(
    title = "TP53 Expression by Age Group",
    subtitle = "Patients categorized as Young (<50) or Old (≥50)",
    x = "Age Group",
    y = "TP53 Expression Level",
    fill = "Age Group"
  ) +
  theme_classic()

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)