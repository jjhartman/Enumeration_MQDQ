library(knitr)
library(kableExtra)

#---------------------------------
# no exclusions, enumerativeness == 1
#---------------------------------
author_table <- function(df, note =  ""){
  save_to <- file.path("tables", paste0(unique(df$folder), note, "_authortable.html"))
  message("Saving to ", save_to)
  
  df %>%
    select(author_name, date, enumerativeness_rate1, enumerativeness_rate8, n, one_count, high_count) %>% 
    unique() %>%
    arrange(desc(enumerativeness_rate1)) %>% 
    kable(format = "html") %>%
    kable_styling(font_size = 10) %>%
    save_kable(file = save_to, self_contained = T)
  # You can open this html file in Word, and it will be an editable table there. 
}

author_table(no_ex)

author_table(supplement, note = "_PhalecianHendecasyllables")



