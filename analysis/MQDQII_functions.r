# functions for use in MQDQII analysis

read_csv_folder <- function(dir, debug = FALSE){
  # read all of the csv files in a folder and compile into one dataframe
  
  # the readr package is required for this function to work
  # if it's not found, use install.packages("readr")
  stopifnot(require(readr))
  
  # the list of all files in the given directory
  files <- list.files(dir, pattern = "*.csv$")
  
  for(file in files){
    
    # if in debug mode, print which file is being read
    if(debug) message(file)
    
    # for each file in the directory, read it in as a df
    this_df <- readr::read_csv(file.path(dir, file), show_col_types = debug)
    # add a column recording the file name, just in case
    this_df$file <- file
    # add a column recording the directory name, just in case
    this_df$folder <- dir
    
    if(file == files[1]){
      # if this is the very first file in the directory...
      # save this_df as df
      df <- this_df
    } else {
      # otherwise, append this df to the growing df of all files
      df <- rbind(df, this_df)
    }
  } # end of for loop

  # output of the function is the df object
  return(df)    
}

convert_years <- function(df, col = "author_date", date_corrections){
  # takes a vector of super messy Roman dates and converts to usable year ranges
  
  # this function requires the tidyr, styringr, and dplyr packages to run
  # if it's not available, use install.packages("tidyr", "stringr", "dplyr")
  stopifnot(require(tidyr))
  stopifnot(require(stringr))
  stopifnot(require(dplyr))
  
  # strip extra white space
  date_corrections <- mutate(date_corrections, 
                             min = str_trim(min, side = "both"),
                             max = str_trim(max, side = "both"))
  
  df_clean <- df %>% 
    # split the date column on hyphens, to generate a first pass min and max year
    separate(col = col, into = c("min", "max"), sep = "-", fill = "right") %>% 
    # strip extra white space
    mutate(min = str_trim(min, side = "both"),
           max = str_trim(max, side = "both")) %>% 
    # join date_corrections file
    left_join(date_corrections, by = c("min", "max", "author_name", "file")) %>% 
    rename(date = `New Date`) %>% 
    select(-c(min, max))
  
  return(df_clean)
}

