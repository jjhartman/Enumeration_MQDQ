from cltk import NLP
from cltk.sentence.lat import LatinPunktSentenceTokenizer
from collections import Counter
import itertools
import re

cltk_nlp = NLP(language="lat")

# this tokenizer is used to group words into sentences (rather than lines), to improve accuracy of tokenization
sentence_tokenizer = LatinPunktSentenceTokenizer()


def prepare_input_text(text: str) -> str:
  '''Remove certain punctuation from a string to prepare it for parsing using
  CLTK.

  Create a single, combined string for CLTK, in order to increase the accuracy
  of tokenization. Also remove certain punctuation marks (e.g., <...>), which
  are used in some texts from MQDQ (in early tests, CLTK was treating words
  that started with '<' as verbs, even when it shouldn't have).
  Also remove quotes, which cause an error,
  'CLTKException: Reference: Unrecognized value for UD feature NumForm'.

  Args:
    text: A string to be processed.
  '''

  # remove problematic punctuation
  punct_removed= re.sub('[<>\[\]\(\)\'\"\*]', '', text)

  # remove all non-ASCII characters (e.g. Greek words)
  # note that this removes non-Greek unicode as well 
  # (it will remove everything not found here https://www.w3schools.com/charsets/ref_html_ascii.asp)
  nonascii_removed = re.sub(r'[^\x00-\x7F]', '', punct_removed)

  # delete extra white space (extra white space is introduced by removing Greek words)
  # delete doubled spaces (make them just a single space)
  space_removed = re.sub(r'\s+', ' ', nonascii_removed)
  # delete spaces that occur before a comma (this happens where a word has been removed)
  clean_text = re.sub(' ,', ',', space_removed)


  return clean_text

def tokenize_latin(input_text):
  '''Take input text in Latin, and output an array of dicts that include
    lemmas and parts of speech.

  Args:
    input_text: A list of text lines.
    
  Output: A generator that produces a list (one element per input line) of 
  dicts, each of which comprises:
      - 'text': The original input string from the line
      - 'text_parsed': A string collating the text with its parsed part of
        speech.
      - 'tags': A list (one element per token) of dicts, each of which 
        comprises:
          - 'string': The original token string
          - 'lemma': The lemma of the string
          - 'pos': The Part of Speech of the string in the original text
  '''
  # Break into sentences, *possibly* to speed up processing (vs.
  # processing potentially hundreds of lines of text at once), and
  # to avoid running out of memory for long passages:
  sentences = sentence_tokenizer.tokenize(' '.join(input_text))

  tags_generator = (
      cltk_nlp.analyze(text=prepare_input_text(s)) for s in sentences)
  staged_tags = []

  for line in input_text:
    relevant_tags = []
    line_prepared = prepare_input_text(line)

    # Reconstruct the original lines from the tags as the parser has split
    # them:
    # To do this, we will iterate through tokens until the original text (with
    # whitespace removed) matches a collection of concatenated tokens.
    # This approach seems necessary because CLTK sometimes includes punctuation
    # marks with word tokens, and sometimes does not, making it difficult to
    # match tokens with their original lines based on, e.g., length of the
    # original line's text.

    line_combined = re.sub(r'\s', '', line_prepared)

    line_is_reconstructed = False
    while line_is_reconstructed != True:
      if ''.join([x.get('string') for x in relevant_tags]) != \
          line_combined:
        # CDB testing: next line
        # print (line_combined)
        if len(staged_tags) == 0:
          # CDB testing: next line
          # print (staged_tags)

          cltk_doc = next(tags_generator)

          staged_tags += [{
            'string': x.string,
            'lemma': x.lemma,
            'pos': str(x.pos),
            'case': {str(key): [str(case_value) for case_value in value] for \
              key, value in x.features.features.items()}.get('Case')
          } for x in cltk_doc.words]

          # breakpoint()

        relevant_tags.append(staged_tags[0])
        del staged_tags[0]
      else:
        line_is_reconstructed = True

        # Create a plain-text string interspersing the original text with the
        # part of speech, etc.:
        line_with_parsing = ' '.join(
            [f'{x["string"]} [{x["pos"]}{", " + ", ".join(x["case"]) + " case" if x["case"] is not None else ""}]' for x in relevant_tags])

        yield {
            'text': line,
            'text_parsed': line_with_parsing,
            'tags': relevant_tags,
        }


def enumerativeness(
  parsed_line: list,
  excluded_parts_of_speech:list = [],
  exclude_special = True
  ) -> float:
  '''Calculate the "enumerativeness" of a line of poetry. Enumerativeness is defined as the ratio of the number of words in the most represented case
  in the line to the number of total words in the line (optionally limited to
  specific parts of speech).

  Args:
    parsed_line: A list for a single line, generated by tokenize_latin(). It
    should have the following form:

      {
        'text': 'Quas habet Indus Arabs Geta Thrax Persa Afer Hiberus,',
        'text_parsed': 'Quas [pronoun, accusative case] habet [verb] Indus [noun, nominative case] Arabs [proper_noun, nominative case] Geta [noun, nominative case] Thrax [proper_noun, nominative case] Persa [noun, nominative case] Afer [noun, nominative case] Hiberus [noun, nominative case] , [punctuation]',
        'tags': [
          {
            'string': 'Quas',
            'lemma': 'iuo',
            'pos': 'pronoun',
            'case': ['accusative']
          },
          {
            ...
          }
        ]
      }

    excluded_parts_of_speech: A list of Part of Speech tags from
    parsed_line.tags[*].pos to use to exclude tokens from input_line when
    calculating "enumerativeness" (note that pos "punctuation" is excluded regardless, this is just to exclude additional pos)
    
    exlude_special: exclude lines with special characters (usually Greek)? Defaults to True. 

  Output: A float, representing the enumerativeness of the line.
  '''
  # if exclude_special and bool(re.match('[α-ωΑ-Ω]', parsed_line.get('text'))):
  #   print("\n***GREEK***\n")

  #   # exclude lines with special characters (e.g. Greek)
  #   return(None)
  
  # else :

  cases = list(itertools.chain.from_iterable(
    [tag.get('case', []) for tag in parsed_line.get('tags') if \
      tag.get('pos') not in excluded_parts_of_speech and \
        tag.get('case') is not None]))

  case_counter = Counter(cases)
  top_count_token_case = case_counter.most_common(1)[0][1] if \
      len(case_counter) > 0 else 0

  line_words = len([str(x['pos']) for x in parsed_line.get('tags') if str(
      x['pos']) != 'punctuation'])

  line_words_limited = len([str(x['pos']) for x in parsed_line.get(
      'tags') if str(x['pos']) != 'punctuation' and
      not any(excluded_pos in x['pos'] for excluded_pos in excluded_parts_of_speech)])

  enumerativeness_dict = {"top_case" : top_count_token_case, "tokens" : line_words_limited, "enumerativeness" : round(top_count_token_case / line_words_limited, 3) if line_words_limited > 0 else None}

  return enumerativeness_dict
