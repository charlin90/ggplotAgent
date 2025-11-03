library(tidyverse)
library(ggrepel)

data <- read.csv("__INPUT_FILE__")

final_plot <- ggplot(data = data) +
  geom_point(aes(x = EGFR_expr, y = KRAS_expr, color = drug_response),
             size = 3, alpha = 0.7) +
  scale_color_manual(
    values = c("Responder" = "#1f77b4", "Non-responder" = "#ff7f0e"),
    name = "Drug Response"
  ) +
  theme_classic() +
  labs(
    title = "Relationship Between EGFR and KRAS Expression",
    subtitle = "Colored by Drug Response Status",
    x = "EGFR Expression Level",
    y = "KRAS Expression Level",
    caption = "Data from patient tumor samples"
  )

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)