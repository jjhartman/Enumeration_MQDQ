import csv
import dask.dataframe as dd
import json
import logging
import os
import pandas as pd
from cltk.sentence.lat import LatinPunktSentenceTokenizer
import json
import logging
import os

import tokenize_latin

logger = logging.getLogger('mqdq_tokenization')
logging.basicConfig()

sentence_tokenizer = LatinPunktSentenceTokenizer()


def mqdq_to_enumerativeness_dataframe(
    data: str,
    allowed_meters: list = None,
    excluded_parts_of_speech:list = [],
    batch_size: int = 10) -> None:
  '''A wrapper function for taking an input JSON file of Latin poetry
  and parsing its lines.

  Args:
    data: Data read from output that was created by
    download_mqdq_author_works.download_mqdq_author_works(). Should have
    the following form:

      {
        "author_name": null,
        "author_date": "peruetusta",
        "author_id": 1,
        "author_url": "http://mizar.unive.it/mqdq/public/indici/autori/idAuthors/1",
        "author_works": [
          {
            "name": "carminum Saliarium reliquiae",
            "edition": "(J. Bl\u00e4nsdorf, FPL, 2011)",
            "sections": [
              {
                "href": "http://mizar.unive.it/mqdq/public/testo/testo/codice/CARM_SAL%7Cfrag%7C001",
                "meter": "Archaic verses",
                "lines": [
                  "Diuum \u2020empta cante, diuum deo supplicate"
                ]
              }
            ]
          }
        ]
      }

     allowed_meters: "Meters" values from MQDQ to allow. Defaults to None,
        which allows everything.

    excluded_parts_of_speech: arguyment to be passed to tokenize_latin.enumerativeness    
    
    batch_size: The number of output parsed lines to batch before yielding.
      Defaults to 10.

  Output: A generator of rows from a Pandas DataFrame, with the following
    headers:
      text, text_parsed, tags, line_number, author_name, author_date,
      author_id, work_name, work_edition, section_url, section_meter

  '''
  # logger.info('Opening "%s"...', data_file)
  # with open(data_file) as f:
  #     data = json.load(f)

  for work in data.get('author_works'):
    filtered_sections = [s for s in work.get('sections', []) if s.get(
        'meter') in allowed_meters] if allowed_meters is not None else [
        s for s in work.get('sections', [])]

    if not len(filtered_sections) > 0:
        logger.info(
            'No sections of this work met filter criteria. Moving on...')
        continue

    for section in filtered_sections:
      finished_parsing = False
      logger.info(
          'Processing section with href "%s"...', section.get('href'))

      parsing_generator = tokenize_latin.tokenize_latin(
          section.get('lines', []))
      # Write the output file in batches
      i = 0
      overall_i = 0
      parsed_lines = []
      while finished_parsing is not True:
        logging.info(
            'Parsing next sentence for section with href "%s"...',
            section.get('href'))
        try:
          new_line = next(parsing_generator)
          enumerativeness_dict = tokenize_latin.enumerativeness(new_line, excluded_parts_of_speech=excluded_parts_of_speech)
          new_line.update(
              {'line_number': overall_i, 'enumerativeness': enumerativeness_dict["enumerativeness"], 'tokens':enumerativeness_dict["tokens"], 'top_case': enumerativeness_dict["top_case"]})
          parsed_lines.append(new_line)
        except StopIteration:
          finished_parsing = True
        if i >= batch_size - 1 or finished_parsing is True:
          logger.info('Yielding batch of lines...')

          parsed_lines_df = pd.json_normalize(parsed_lines)
          parsed_lines_df['author_name'] = data.get('author_name')
          parsed_lines_df['author_date'] = data.get('author_date')
          parsed_lines_df['author_id'] = data.get('author_id')
          parsed_lines_df['work_name'] = work.get('name')
          parsed_lines_df['work_edition'] = work.get('edition')
          parsed_lines_df['section_url'] = section.get('href')
          parsed_lines_df['section_meter'] = section.get('meter')

          i = 0
          parsed_lines = []
          yield parsed_lines_df

        i += 1
        overall_i += 1

  return


# with open(
#   '/home/jacoblevernier/go/src/github.com/jjhartman/mqdq-text1/124.json') as f:
#   data = json.load(f)
# test = mqdq_to_enumerativeness_dataframe(
#   data,
#   batch_size=10
# )


def mqdq_to_csv(
        data_file: str,
        output_file: str,
        allowed_meters: list = None,
        excluded_parts_of_speech:list = [],
        write_lines: int = 10) -> None:
  '''A wrapper function for taking an input JSON file of Latin poetry, parsing
  its lines, and writing the output to a CSV file.

  Args:
    data_file: The filename of a JSON file, to pass to 
      mqdq_to_enumerativeness_dataframe. See the help documentation for
      mqdq_to_enumerativeness_dataframe for more detail on the expected format
      of this file.

    output_file: The name of a file to write to. Output will be written
      as CSV.

    allowed_meters: "Meters" values from MQDQ to allow, to pass to
      mqdq_to_enumerativeness_dataframe.

    excluded_parts_of_speech: to be passed to tokenize_latin.enumerativeness within call to mqdq_to_enumerativeness_dataframe 

    write_lines: The number of output parsed lines to batch before writing to
      output_file. Defaults to 10.

  Output: None. This function will write to output_file, comprising a CSV with
    headers:
      text, text_parsed, tags, line_number, author_name, author_date,
      author_id, work_name, work_edition, section_url, section_meter

  '''
  logger.info('Opening "%s"...', data_file)
  with open(data_file) as f:
      data = json.load(f)

  output_directory = os.path.dirname(output_file)

  if output_directory != '' and not os.path.exists(output_directory):
    logger.info(
        'Creating directory "%s" for output...', output_directory)
    os.makedirs(output_directory)

  output_file_exists = os.path.isfile(output_file)
  write_header = True if not output_file_exists else False
  existing_output = dd.read_csv(output_file) if output_file_exists else None

  row_generator = mqdq_to_enumerativeness_dataframe(
    data,
    batch_size=write_lines,
    allowed_meters=allowed_meters,
    excluded_parts_of_speech=excluded_parts_of_speech
  )
  
  for batch in row_generator:
    # Discard rows that are already present in output_file, and write the
    # remaining lines to output_file:
    # if existing_output is not None:
    #   breakpoint()
    #   batch = batch[~batch.isin(existing_output)].dropna(how='all')
    batch.to_csv(
      output_file,
      mode='a',
      header=write_header,
      quoting=csv.QUOTE_NONNUMERIC,
      index=False)
    write_header = False


  # for work in data.get('author_works'):
  #   filtered_sections = [s for s in work.get('sections', []) if s.get(
  #       'meter') in allowed_meters] if allowed_meters is not None else [
  #       s for s in work.get('sections', [])]

  #   if not len(filtered_sections) > 0:
  #       logger.info(
  #           'No sections of this work met filter criteria. Moving on...')
  #       continue

  #   for section in filtered_sections:
  #     finished_parsing = False
  #     logger.info(
  #         'Processing section with href "%s"...', section.get('href'))

  #     if existing_output is not None:
  #       existing_lines_parsed = existing_output[
  #           existing_output.section_url == section.get('href')].size.compute()

  #       if len(section.get('lines', [])) == existing_lines_parsed:
  #         logger.info(
  #             ('Processing section with href "%s"... is already complete. '
  #              'Moving on...'), section.get('href'))
  #         continue
  #       else:
  #         logger.info('Section with href "%s" incomplete. Restarting it...',
  #                     section.get('href'))
  #         # Restart the section. We can't restart it midway, because lines !=
  #         # sentences, which are used to parse:
  #         data_to_overwrite = dd.read_csv(output_file)

  #         data_to_overwrite = data_to_overwrite[
  #             data_to_overwrite.section_url != section.get('href')
  #         ]
  #         data_to_overwrite.to_csv(
  #             output_file,
  #             single_file=True,
  #             header=True,
  #             quoting=csv.QUOTE_NONNUMERIC,
  #             index=False,
  #             mode='w'
  #         )

  #     parsing_generator = tokenize_latin.tokenize_latin(
  #         section.get('lines', []))data_file
  #     # Write the output file in batches
  #     i = 0
  #     overall_i = 0
  #     parsed_lines = []
  #     while finished_parsing is not True:
  #       logging.info(
  #           'Parsing next sentence for section with href "%s"...',
  #           section.get('href'))
  #       try:
  #         new_line = next(parsing_generator)
  #         new_line.update({'line_number': overall_i})
  #         parsed_lines.append(new_line)
  #       except StopIteration:
  #         finished_parsing = True
  #       if i == write_lines - 1 or finished_parsing is True:
  #         logger.info(f'Saving batch of lines to "{output_file}"...')

  #         parsed_lines_df = pd.json_normalize(parsed_lines)
  #         parsed_lines_df['author_name'] = data.get('author_name')
  #         parsed_lines_df['author_date'] = data.get('author_date')
  #         parsed_lines_df['author_id'] = data.get('author_id')
  #         parsed_lines_df['work_name'] = work.get('name')
  #         parsed_lines_df['work_edition'] = work.get('edition')
  #         parsed_lines_df['section_url'] = section.get('href')
  #         parsed_lines_df['section_meter'] = section.get('meter')
  #         parsed_lines_df.to_csv(
  #             output_file,
  #             mode='a',
  #             header=write_header,
  #             quoting=csv.QUOTE_NONNUMERIC,
  #             index=False)

  #         write_header = False

  #         i = 0
  #         parsed_lines = []
  #         continue

  #       i += 1
  #       overall_i += 1

  return


# mqdq_to_csv(
#     data_file='/home/jacoblevernier/go/src/github.com/jjhartman/mqdq-text1/124.json',
#     output_file=os.path.join('parsed_data', '124.csv'),
#     write_lines=10
# )
