library(tidyverse)
library(ggrepel)

data <- read.csv("__INPUT_FILE__")

preprocessed_data <- data %>%
  select(patient_id, drug_response, TP53_expr, BRCA1_expr) %>%
  pivot_longer(
    cols = c(TP53_expr, BRCA1_expr),
    names_to = "gene",
    values_to = "expression"
  ) %>%
  mutate(gene = str_remove(gene, "_expr")) %>%
  mutate(gene = factor(gene, levels = c("TP53", "BRCA1")))

final_plot <- ggplot(preprocessed_data, aes(x = drug_response, y = expression)) +
  geom_boxplot(aes(fill = drug_response), 
               width = 0.6,
               outlier.shape = NA) +
  geom_jitter(aes(color = drug_response),
              width = 0.2,
              alpha = 0.6,
              size = 2) +
  facet_wrap(~ gene, scales = "fixed", ncol = 2) +
  scale_fill_manual(values = c("Responder" = "#66c2a5", 
                              "Non-responder" = "#fc8d62")) +
  scale_color_manual(values = c("Responder" = "#1b9e77", 
                               "Non-responder" = "#d95f02")) +
  theme_classic() +
  theme(
    strip.background = element_blank(),
    strip.text = element_text(face = "bold", size = 12),
    legend.position = "top"
  ) +
  labs(
    x = "Drug Response",
    y = "Gene Expression Level",
    title = "Comparison of BRCA1 and TP53 Expression",
    subtitle = "Between Responders and Non-responders",
    fill = "Response Status",
    color = "Response Status"
  )

ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)
ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)