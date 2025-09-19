'''Having downloaded files using 
download_mqdq_author.download_mqdq_author_works(), transform those files into
CSVs, tokenizing the text contained in them along the way.

This script will process multiple files simultaneously, depending on the number
of available cores.
'''

import dask.dataframe as dd
from glob import glob
import json
import logging
import multiprocessing
import os
import pandas as pd
import psutil
import datetime

import create_csvs

logger = logging.getLogger('mqdq_tokenization')
logging.basicConfig()
logger.setLevel(logging.DEBUG)

number_of_cores = psutil.cpu_count(logical=True)

data_directory = '/Users/joshuahartman/desktop/MQDQII/Temporary_Texts'
output_directory = 'CSVS_No_Exclusion'

# set the excluded parts of speech here
excluded_parts_of_speech = []


# Only process files that have not already been processed:
files_to_process = [f for f in glob(os.path.join(
    data_directory, '*.json')) if not os.path.exists(
    os.path.join(output_directory,
                 f'{os.path.splitext(os.path.basename(f))[0]}.csv'))]

# write a log file to capture parameters for  this run
current_date_and_time = datetime.datetime.now()
current_date_and_time_string = str(current_date_and_time)
log_file = "_log_" +  current_date_and_time_string + ".txt"
log = open(os.path.join(output_directory, log_file), "a")

log.write(output_directory + "\n")
log.write("excluded parts of speech: " + ' '.join([str(elem) for elem in excluded_parts_of_speech]) + "\n")
log.write("Files: " + ' '.join([str(elem) for elem in files_to_process]) + "\n\n")

# copy over the current version of each py file used
cc = open("create_csvs.py", "r")
log.write("\n\n*****************\n create_csvs.py \n*****************\n")
for line in cc:
    log.write(line)
cc.close()
tl = open("tokenize_latin.py", "r")
log.write("\n\n*****************\n tokenize_latin.py \n*****************\n")
for line in tl:
    log.write(line)
tl.close()

log.close() # close the log file




for file in files_to_process:

    create_csvs.mqdq_to_csv(
        data_file=file,
        output_file=os.path.join(output_directory, 
            f'{os.path.splitext(os.path.basename(file))[0]}.csv'),
        excluded_parts_of_speech = excluded_parts_of_speech,
        write_lines=10
    )


# '''
# enhance_mqdq_downloaded_data(
#   '/home/jacoblevernier/go/src/github.com/jjhartman/mqdq-text1/036.json',
#   '/home/jacoblevernier/go/src/github.com/jjhartman/mqdq-text1-output/036.json',
#   10
# )
# '''


# def enhance_mqdq_downloaded_data_wrapper(f: str) -> None:
#   '''A wrapper for create_csvs.mqdq_to_csv, to allow setting static additional
#   arguments.

#   Args:
#     f: A filename to pass to create_csvs.mqdq_to_csv
#   '''
#   enhance_mqdq_downloaded_data(
#       f,
#       os.path.join(
#         '/home/jacoblevernier/go/src/github.com/jjhartman/mqdq-text1-output',
#         os.path.basename(f)),
#       1)
#   return

# '''
# logger.info("Starting Pool...")
# with multiprocessing.Pool(number_of_cores-1) as p:
#   p.map(
#       enhance_mqdq_downloaded_data_wrapper,
#       files_to_process
#   )
# '''


# def mqdq_to_csv_wrapper(f: str) -> None:
#   '''A wrapper for create_csvs.mqdq_to_csv, to allow setting static additional
#   arguments.

#   Args:
#     f: A filename to pass to create_csvs.mqdq_to_csv
#   '''
#   create_csvs.mqdq_to_csv(
#       f, output_data_directory=output_directory, allowed_meters=['Hexameters'])
#   return

# logger.info("Starting Pool...")
# with multiprocessing.Pool(number_of_cores-1) as p:
#   p.map(
#       mqdq_to_csv_wrapper,
#       files_to_process
#   )

# create_csvs.mqdq_to_csv(
#   '/home/jacoblevernier/go/src/github.com/jjhartman/mqdq-text1/124.json',
#   excluded_parts_of_speech = [],
#   output_data_directory=output_directory,
#   allowed_meters=['Hexameters']
# )
