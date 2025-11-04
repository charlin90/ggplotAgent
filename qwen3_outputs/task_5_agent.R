library(tidyverse)
library(ggrepel)

# Read the input data
data <- read.csv("__INPUT_FILE__")

# Create the final plot
final_plot <- ggplot(data, aes(x = EGFR_expr, y = KRAS_expr, color = drug_response)) +
  geom_point() +
  scale_color_manual(values = c("Responder" = "blue", "Non-responder" = "red")) +
  theme_classic() +
  labs(
    title = "Relationship Between EGFR and KRAS Expression by Drug Response",
    x = "EGFR Expression (log2 scale)",
    y = "KRAS Expression (log2 scale)",
    color = "Drug Response"
  )

# Save the plot in PNG and PDF formats
ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)