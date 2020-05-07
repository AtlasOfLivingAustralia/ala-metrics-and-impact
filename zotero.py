from pyzotero import zotero
import pandas as pd
import config
import requests

library_id = config.LIBRARY_ID
api_key = config.ZOTERO_API_KEY
library_type = 'group'

def retrieve_zotero_data():
    all_data = pd.DataFrame()
    zot = zotero.Zotero(library_id, library_type, api_key)
    # get number of items
    item_count = zot.num_items()

    # get first 100 items
    items = zot.top(limit=100)
    # extract data and get all subsequent items
    for i in range(item_count // 100 + 1):
        for i in items:
            if is_relevant_item(i):
               row = extract_item_data(i['data'])
               all_data = all_data.append(pd.Series(row), ignore_index=True)
        try:
            items = zot.follow(limit = 100)
        except requests.exceptions.ConnectionError:
            break

    all_data.to_csv('zotero_data.csv', index=False)

def extract_item_data(data):
    row = {
        'key': data['key'],
        'type': data['itemType']
    }

    # additional fields
    row['creators'] = format_creators(data['creators']) if 'creators' in data.keys() else ""
    row['title'] = data['title'] if 'title' in data.keys() else ""
    row['publicationTitle'] = data['publicationTitle'] if 'publicationTitle' in data.keys() else ""
    row['date'] = data['date'] if 'date' in data.keys() else ""
    row['libraryCatalog'] = data['libraryCatalog'] if 'libraryCatalog' in data.keys() else ""
    row['DOI'] = data['DOI'] if 'DOI' in data.keys() else ""
    row['ISBN'] = data['ISBN'] if 'ISBN' in data.keys() else ""
    row['ISSN'] = data['ISSN'] if 'ISSN' in data.keys() else ""
    row['extra'] = data['extra'] if 'extra' in data.keys() else ""
    row['tags'] = format_tags(data['tags']) if 'tags' in data.keys() else ""

    return row

def is_relevant_item(item):
    if item['data']['itemType'] == 'journalArticle' or item['data']['itemType'] == 'conferencePaper':
        return True
    return False

def format_creators(creators):
    creator_list = []
    for c in creators:
        fn = c['firstName'] if 'firstName' in c.keys() else ''
        ln = c['lastName'] if 'lastName' in c.keys() else ''
        creator_list.append(fn + " " + ln)

    return creator_list

def format_tags(tags):
    tag_list = []
    for t in tags:
        tag_list.append(t['tag'])
    return tag_list
