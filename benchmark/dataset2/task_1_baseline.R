library(tidyverse)
library(ggrepel)

data <- read.csv("bio_data_master.csv")

final_plot <- ggplot(data, aes(x = base_mean_expr)) +
  geom_histogram(bins = 30, fill = "steelblue", color = "white", alpha = 0.8) +
  labs(title = "Distribution of Base Mean Expression",
       x = "Base Mean Expression",
       y = "Count") +
  theme_minimal() +
  theme(plot.title = element_text(hjust = 0.5, face = "bold"))

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)