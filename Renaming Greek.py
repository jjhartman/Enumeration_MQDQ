import os
import re
import glob
import itertools
import json
import re
import unidecode

# create list in order to begin for loop
files=glob.glob("*.json")

#setup for loop to go through each csv  in dir and find  the Greek  chars
for file in files:
  #open file, read mode
  file_conn=open(file,"r")
  json_contents = json.load(file_conn)
  file_conn.close()

  for i, work in enumerate(json_contents['author_works']):
    for j, section in enumerate(work['sections']):
      for k, line in enumerate(section['lines']):
        json_contents['author_works'][i]['sections'][j]['lines'][k] = unidecode.unidecode(line)

  file_conn=open(file,"w")
  json.dump(json_contents, file_conn, indent=2, ensure_ascii=True)
  file_conn.close()