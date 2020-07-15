from pyzotero import zotero
import pandas as pd
import config
import requests
import sys
import re

# library_id = config.LIBRARY_ID
# api_key = config.ZOTERO_API_KEY
# library_type = 'group'

def retrieve_data(library_id, api_key, library_type, outfile):
    all_data = pd.DataFrame()
    zot = zotero.Zotero(library_id, library_type, api_key)
    # get number of items
    item_count = zot.num_items()

    # get first 100 items
    items = zot.top(limit=100)
    # extract data and get all subsequent items
    for i in range(item_count // 100 + 1):
        for i in items:
            row = extract_item_data(i['data'])
            all_data = all_data.append(pd.Series(row), ignore_index=True)
        try:
            items = zot.follow(limit = 100)
        except requests.exceptions.ConnectionError:
            break
    # return all_data
    all_data.to_csv(outfile, index=False)

def extract_item_data(data):
    row = {
        'key': data['key'],
        'type': format_item_type(data['itemType'])
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
    row['tags'] = format_one_line_tags(data['tags']) if 'tags' in data.keys() else ""
    tags = format_tags(data['tags']) if 'tags' in data.keys() else {}
    row = {**row, **tags}

    return row

def format_item_type(type):
    if type == 'document':
        return 'Document - other'
    elif type == 'radioBroadcast':
        return 'Radio broadcast'
    return re.sub("([a-z])([A-Z])","\g<1> \g<2>",type).title()

def format_creators(creators):
    creator_list = []
    for c in creators:
        fn = c['firstName'] if 'firstName' in c.keys() else ''
        ln = c['lastName'] if 'lastName' in c.keys() else ''
        creator_list.append(fn + " " + ln)

    return creator_list

# tag values are zero by default, 1 if the tag is present
def format_tags(tags):
    tag_dict = {'ALA used': 0,
                'ALA cited': 0,
                'ALA discussed': 0,
                'ALA acknowledged': 0,
                'ALA mentioned': 0,
                'ALA author': 0,
                'ALA Data DOI': 0,
                'ALA GBIF DOI': 0,
                'ALA published': 0,
                'TBC': 0,
                'Map': 0}
    for t in tags:
        if t['tag'] in tag_dict.keys():
            tag_dict[t['tag']] = 1
        else:
            try:
                k = t['tag'].split(' - ')[1]
                if k in tag_dict.keys():
                    tag_dict[k] = 1
            except (IndexError,KeyError):
                print(f'Tag: \"{t["tag"]}\" found but not counted')

    return tag_dict

def format_oneline_tags(tags):
      tag_list = []
      for t in tags:
          tag_list.append(t['tag'])
      return tag_list

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Error: Please provide a path to an output file')
        exit()
    outfile = sys.argv[1]
    retrieve_data(config.LIBRARY_ID,config.ZOTERO_API_KEY,'group',outfile)
