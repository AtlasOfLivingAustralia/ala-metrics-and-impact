''' Script to generate list of publications not yet in GBIF.
    Takes a csv of publications in zotero, a csv of publications found by gbif,
    and a list of publications to ignore. Outputs a csv of new publications
'''
import sys
import pandas as pd
import numpy as np


def main():
    zot_pubs = pd.read_csv(sys.argv[1])
    gbif_pubs = pd.read_csv(sys.argv[2])
    ignore_pubs = pd.read_csv(sys.argv[3])

    # Find publications in gbif_pubs but not in zot_pubs
    zot_keys = zot_pubs['archive'].tolist()
    gbif_keys = gbif_pubs['id'].tolist()
    ignore_keys = ignore_pubs['GBIF key'].to_list()

    # keys in gbif but not in zotero
    new_pub_keys = [x for x in np.setdiff1d(gbif_keys,zot_keys) if x not in ignore_keys]
    new_pubs = gbif_pubs[gbif_pubs['id'].isin(new_pub_keys)]
    new_pubs.to_csv('new_publications.csv', index = False)


if __name__ == '__main__':
    main()
