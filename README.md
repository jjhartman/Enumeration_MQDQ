

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7508688.svg)](https://doi.org/10.5281/zenodo.7508688)

# Running this code

1. Confirm that [Python 3.7](https://legacy.cltk.org/en/latest/installation.html#with-pip) and [`virtualenv`](https://docs.python.org/3/tutorial/venv.html) are installed.
1. In a terminal, in the directory of this repo, run `python3 -m virtualenv python_virtualenv` to create a virtualenv. To specify a specific Python version, you can use, for example, `python -m virtualenv --python=/usr/bin/python3.7 python_virtualenv`, where the path to Python is from running `python` followed by two Tabs (to see all python versions that are installed), followed by, e.g., `which python3.7` to see where `python3.7` specifically is installed.
1. In a terminal, in the directory of this repo, activate the virtualenv with `source python_virtualenv/bin/activate`
  1. Install dependencies with `pip3 install -r requirements.txt`

## Tests

You can run unit tests with `python3 -m unittest tests`

# Provenance

## Data

Data are from http://mizar.unive.it/mqdq/public, which includes the following rights note in the footer of each page:

<blockquote>
  Copyright © 2007 — Musisque Deoque
  All rights reserved
  

  All rights of the texts with critical apparatus contained inside www.mqdq.it are reserved to the Musisque Deoque National Interests’ Projects Research, to the editors of the literary word and to the authors of the original documents.

  It is not allowed for any kind of commercial use without prior agreement. Reproductions and circulations in printed format or electronic format (offline) are allowed only to the exclusive scientific, didactical and documentary use, as long as these documents are not altered in any substantial way, and, in particular, are kept with correct indications of date, paternity and original source (by quotation).

  Link from other websites are welcome, especially if the editing will be informed to the editorial board (info@lutessa.it) so as to facilitate the timely communication of following possible variations.

  Any kind of mirroring (duplications) on other sites is forbidden. Any automatic capture of the texts on other sites, without specifics agreement with the editorial board, is also forbidden.
</blockquote>
