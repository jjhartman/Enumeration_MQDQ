# load required libraries
library(tidyverse)
library(knitr)
library(kableExtra)


# load the functions written for this project
source("MQDQII_functions.r")



# ------------------------------------------------------
# read in the data files
# ------------------------------------------------------


# note, set debug = TRUE to get more info as it processes
no_ex_raw <- read_csv_folder("CSVS_No_Exclusion", debug = FALSE)

# save all the section meters as a table
no_ex_raw %>% 
  select(author_name, work_name, section_meter) %>% 
  unique() %>% 
  arrange(section_meter) %>% 
  kable(format = "html") %>%
  kable_styling(font_size = 10) %>%
  save_kable(file = file.path("tables", "meter_table_no_ex.html"), self_contained = T)
# You can open this html file in Word, and it will be an editable table there. 


# ------------------------------------------------------
# clean the data
# ------------------------------------------------------

# read in the csv for cleaning the meters
meter_corrections <- read_csv("meter_cleaning.csv")

# define code for cleaning and filtering the data
cleaning <- function(df, tokens_threshold =  3, lines_threshold = 500, included_meters=c("Hexameters", "Elegiac couplets"), date_corrections){
  
  # clean meters 
  df <- df %>% 
    left_join(meter_corrections, by=c("author_name", "work_name", "section_meter")) %>% 
    mutate(section_meter = if_else(is.na(Corrected_meter), section_meter, Corrected_meter)) %>% 
    select(-Corrected_meter)
  
  df <- df %>% 
    # only keep the included meters
    filter(section_meter %in% included_meters) %>% 
    # only keep lines with more than tokens_threshold tokens
    filter(tokens > tokens_threshold)

  
  # get the number of lines in each work
  df_counts <-  count(df, file)
  
  clean_df <- df %>% 
    # join counts to original dataframe
    left_join(df_counts, by = "file") %>% 
    # then filter out works with fewer than lines_threshold lines
    filter(n > lines_threshold) %>% 
    # convert author date years
    convert_years(date_corrections = date_corrections) %>% 
    # calculate number of lines >.8 / total number of lines
    
    mutate(high_enumerativeness = if_else(enumerativeness > .8, 1, 0),
           one_enumerativeness = if_else(enumerativeness == 1, 1, 0)) %>% 
    group_by(file) %>%
    mutate(high_count = sum(high_enumerativeness, na.rm = TRUE),
           one_count = sum(one_enumerativeness, na.rm = TRUE),
           enumerativeness_rate8 = high_count/n,
           enumerativeness_rate1 = one_count/n) %>% 
    ungroup()
    
    
    return(clean_df)
}

date_corrections <- read_csv("dates_cleaning.csv")

# apply cleaning and filtering code 
no_ex <- cleaning(no_ex_raw, date_corrections = date_corrections) 


# supplementary information on Phalecian hendecasyllables
# set tokens_threshold to 0, so no lines are excluded for low tokens
# set lines_threshold to 0, so no authors are excluded for low lines
supplement <- cleaning(no_ex_raw, tokens_threshold =  0, lines_threshold = 0, included_meters="Phalecian hendecasyllables", date_corrections = date_corrections)
