library(tidyverse)
library(ggrepel)

# Read the data
data <- read.csv("bio_complex_data.csv")

# Select relevant columns and pivot longer to get gene expression in long format
expr_data <- data %>%
  select(patient_id, drug_response, BRCA1_expr, TP53_expr) %>%
  pivot_longer(cols = c(BRCA1_expr, TP53_expr),
               names_to = "gene",
               values_to = "expression") %>%
  mutate(gene = recode(gene,
                       BRCA1_expr = "BRCA1",
                       TP53_expr = "TP53"))

# Create the box plot
final_plot <- ggplot(expr_data, aes(x = drug_response, y = expression, fill = drug_response)) +
  geom_boxplot() +
  facet_wrap(~ gene, ncol = 2) +
  theme_classic() +
  labs(x = "Drug Response", y = "Gene Expression") +
  theme(legend.position = "none")

# Save the plot in PNG and PDF formats
ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)