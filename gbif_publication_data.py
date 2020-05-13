import requests
import pandas as pd
import json

GBIF_URL_PREFIX="https://www.gbif.org/api/resource/search?limit=999&contentType=literature&gbifDatasetKey="

DATA_RESOURCES_URL = "https://biocache-ws.ala.org.au/ws/occurrence/facets?facets=data_resource_uid&flimit=1000"
DR_INFO_URL = "https://collections.ala.org.au/ws/dataResource/"


def main():
    i = 0
    publications = []
    keys = retrieve_gbif_registry_keys()
    for k in keys:
        url = GBIF_URL_PREFIX + k
        resp = requests.get(url)
        results = resp.json()['results']
        for r in results:
            id = r['id']
            # attempt to retrieve doi
            if 'identifiers' in r.keys() and 'doi' in r['identifiers'].keys():
                doi = r['identifiers']['doi']
                info = {'id':id,'doi':doi[0]}

            # no doi present so return other information
            else:
                info = {'id':id}

                info['first_author'] = format_author(r['authors']) if 'authors' in r.keys() else ""
                info['source'] = r['source'] if 'source' in r.keys() else ''
                info['title'] = r['title'] if 'title' in r.keys() else ''
                info['year'] = int(r['year']) if 'year' in r.keys() else ''
                info['websites'] = format_websites(r['websites']) if 'websites' in r.keys() else ''
            publications.append(info)

    df = pd.DataFrame(publications)
    df.set_index('id', inplace=True)
    df.fillna('',inplace=True)
    df.to_csv('publications_from_gbif.csv')

    df.drop_duplicates(inplace = True)
    print(len(df))

    df.to_csv('publications_from_gbif.csv')

def format_author(authors):
    if len(authors) == 0:
        return ''
    fn = authors[0]['firstName'] if 'firstName' in authors[0].keys() else ''
    ln = authors[0]['lastName'] if 'lastName' in authors[0].keys() else ''
    return fn + " " + ln

def format_websites(websites):
    return ','.join([str(elem) for elem in websites])

def retrieve_gbif_registry_keys():
    keys = []
    resp = requests.get(DATA_RESOURCES_URL)
    dr_info = pd.DataFrame(resp.json()[0]['fieldResult'])
    drs = [x.split('.')[1] for x in list(dr_info['i18nCode'])]

    # retrieve gbif citation key if it exists
    for dr in drs:
        try:
            url = DR_INFO_URL + dr
            resp = requests.get(url)
            key = resp.json()['gbifRegistryKey']
            if key != None:
                keys.append(key)
        except (KeyError,json.decoder.JSONDecodeError):
            print('no key found')
            print(dr)
    return keys

if __name__ == '__main__':
    main()
    # retrieve_gbif_registry_keys()
