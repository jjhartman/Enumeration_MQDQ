# ------------------------------------------------------
# plotting
# ------------------------------------------------------

# set the overall appearance for plots
theme_set(theme_classic())

# define code for generating enumerativeness_rate8 over time plots
plot1 <- function(df, enumerativeness_rate, save=TRUE, fit_curve = NULL){
  
  df <- df %>%
    select(folder, author_name, date, {{enumerativeness_rate}}) %>% 
    unique()
  
  if(colnames(df)[4] == "enumerativeness_rate8"){
    title <- "Number of lines with\nenumerativeness > .8 / total number of lines"
  } else if(colnames(df)[4] == "enumerativeness_rate1") {
    title <- "Number of lines with\nenumerativeness = 1 / total number of lines"
  } else {
    title <- "Unknown enumerativeness rate"
  }
  
  p <- ggplot(df, aes(x=date, y={{enumerativeness_rate}})) + 
    geom_point()  + 
    labs(x = "Year", 
         y = "Enumerativeness Rate",
         title = title)
  
  # add a fit curve, if  requested
  if(!is.null(fit_curve)) p <- p +  stat_smooth(method=fit_curve, color = "black", linetype = 2)
  
  if(save){
    ggsave(file.path("plots", paste0("plot1_", colnames(df)[4], gsub(x=unique(df$folder), pattern = " ", replacement = "_"), ".png")), p, 
           width = 7, height = 6, units = "in")
  }
  return(p)
}


# apply the code for generating enumerativeness_rate over time plots
plot1(no_ex, enumerativeness_rate8, save=TRUE, fit_curve = "lm")
plot1(no_ex, enumerativeness_rate1, save=TRUE, fit_curve = "lm")


# define the code for plotting lines with enumerativeness > .8 or =1 against total lines
plot2 <- function(df, enumerativeness_rate, save = TRUE, log = TRUE, label_authors = 100){
  df <- df %>%
    select(folder, author_name, date, {{enumerativeness_rate}}, n, high_count, one_count) %>% 
    unique()
  
  if(colnames(df)[4] == "enumerativeness_rate8"){
    title <- "Number of lines with\nenumerativeness > .8 / total number of lines"
    cutoff <- ifelse(df$high_count > label_authors, "black", NA)
    
    p <- ggplot(df, aes(x=n, y=high_count))
  } else if(colnames(df)[4] == "enumerativeness_rate1") {
    title <- "Number of lines with\nenumerativeness = 1 / total number of lines"
    
    cutoff <- ifelse(df$one_count > label_authors, "black", NA)
    
    p <- ggplot(df, aes(x=n, y=one_count))
  } else {
    title <- "Unknown enumerativeness rate"
  }
  
  
  p <- p + 
    geom_point()  + 
    labs(x = "Number of lines", 
         y = "Number of high enumerativeness lines",
         title = title) + 
    geom_text(aes(label = author_name), color = cutoff, 
              check_overlap = TRUE, vjust = 0, hjust = 1,
              show.legend = FALSE)
  
  if(log){
    p <- p + scale_x_log10() + 
      labs(x = "Number of lines (log transformed)")
  }
  
   
  if(save){
    ggsave(file.path("plots", paste0("plot2_", colnames(df)[4], gsub(x=unique(df$folder), pattern = " ", replacement = "_"), ".png")), p, 
           width = 10, height = 6, units = "in")
  }
  return(p)
}


plot2(no_ex, enumerativeness_rate8, save=TRUE, log= TRUE, label_authors = 40)
plot2(no_ex, enumerativeness_rate1, save=TRUE, log= TRUE, label_authors = 16)

# enumerativeness by author
author_plot <- function(df, enumerativeness_rate){
  
  df <- df %>%
    select(folder, author_name, date, {{enumerativeness_rate}}) %>% 
    unique()
  
  if(colnames(df)[4] == "enumerativeness_rate8"){
    title <- "Number of lines with\nenumerativeness > .8 / total number of lines"
  } else if(colnames(df)[4] == "enumerativeness_rate1") {
    title <- "Number of lines with\nenumerativeness = 1 / total number of lines"
  } else {
    title <- "Unknown enumerativeness rate"
  }
  
  p <- ggplot(df, aes(y=fct_reorder(author_name, {{enumerativeness_rate}}), fill = date, x = {{enumerativeness_rate}})) + 
    geom_bar(stat = "identity")  + 
    labs(y = NULL, 
         x = title)
  
  ggsave(file.path("plots", paste0("authors_", colnames(df)[4], gsub(x=unique(df$folder), pattern = " ", replacement = "_"), ".png")), p,
         height = 8, width = 8, unit = "in")
  
  return(p)
}

author_plot(no_ex, enumerativeness_rate8)
author_plot(no_ex, enumerativeness_rate1)
