library(tidyverse)
library(ggrepel)

data <- read.csv("bio_complex_data.csv")

final_plot <- ggplot(data, aes(x = EGFR_expr, y = KRAS_expr, color = drug_response)) +
  geom_point(size = 3, alpha = 0.7) +
  labs(title = "Relationship between EGFR and KRAS Expression",
       x = "EGFR Expression",
       y = "KRAS Expression",
       color = "Drug Response") +
  theme_minimal() +
  theme(legend.position = "bottom",
        plot.title = element_text(hjust = 0.5))

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)