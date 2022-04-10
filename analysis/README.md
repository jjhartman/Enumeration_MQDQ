# MQDQII analysis files

## Contents overview

There are three scripts for the analysis (01_cleaning.r, 02_plotting.r, and 03_table.r), to be run in order. 
There is an additional R file, MQDQII_functions.r, which contains functions written specifically for this project and used in the three analysis scripts. 


The scripts are written in such a way that it should (hopefully) be pretty straightforward to extend the analysis to additional folders, should the need arise. 

## Cleaning script

Right now, the cleaning process filters to keep only lines where section_meter is either exactly "Hexameters" or "Elegiac Couplets", which potentially misses a fair amount of useful data. It then filters out any lines with 3 or fewer tokens, under the assumption that lines in the selected meters should almost never have 3 or fewer tokens (such lines are likely due to skipped words, such as Greek words). After excluding irrelevant meters and short lines, then the files are further filtered to only include csvs where the remaining number of lines is at least 500 lines --- files with fewer are excluded. 

Lines are coded for "high_enumerativeness", which is defined as enumerativeness > .8 (after closer examination of the corpus, an alternative cutoff of .75 was considered but abandoned because of the many lines with enumerativeness == .8 because of being composed of 5 tokens). The enumerativeness_rate is then calculated for each csv (after filtering described above), getting the number of high enumerativeness lines / total number of lines in the filtered csv. 

Author year is often specified as an estimate or range. When a range is given, the second number (later year) is used. 
(All ranges were listed as the end of the range, if only a person (author or emperor) is given as a relative date, the end dates for that figure are given.  e.g. aetate Hadriani = 138, amicus Ovidii =18)


## Plotting script

The plotting script produces three kinds of plots: plot1, plot2, and author_plot. 

Plot1 is a scatterplot with year on the x-axis and enumerativeness rate (proportion of lines that count as "highly ennumerative")  on the y-axis, with each author as one observation. 
There is a linear line of best fit to show the overall trend in enumerativeness over time. 

Plot2 is a scatterplot of total number of highly enumerative lines on the y-axis by total number of lines in corpus on the x-axis, with each author as one observation. 
Author names are added as labels for the most enumerative. 
This plot is mostly for exploratory purposes. 

The author_plot is a bar chart with one bar for each author, and bar height corresponding to enumerativeness rate, additionally sorted by enumerativeness rate. 
Each bar is colored by the author's year, so the rough trend in early vs. later authors is apparent. 
This plot is mostly for exploratory purposes. 

Output from the plotting script saves to the `plots` subdirectory.

## Table script

The table script saves information about each author to an html table that  can then be opened in Word. 

Output from the table script saves to the `tables` subdirectory.

