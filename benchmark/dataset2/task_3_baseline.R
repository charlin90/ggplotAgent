library(tidyverse)
library(ggrepel)

data <- read.csv("bio_data_master.csv")

final_plot <- ggplot(data, aes(x = fct_infreq(biotype))) +
  geom_bar(fill = "steelblue") +
  labs(title = "Count of Each Biotype",
       x = "Biotype",
       y = "Count") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)