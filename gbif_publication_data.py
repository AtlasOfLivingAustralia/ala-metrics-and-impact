import requests
import pandas as pd
import json
import logging
from math import isnan

GBIF_URL_PREFIX="https://www.gbif.org/api/resource/search?limit=999&contentType=literature&gbifDatasetKey="
DATASET_SEARCH_URL = "https://www.gbif.org/api/dataset/search?q="


DATA_RESOURCES_URL = "https://biocache-ws.ala.org.au/ws/occurrence/facets?facets=data_resource_uid&flimit=1000"
DATA_PROVIDERS_URL = "https://biocache-ws.ala.org.au/ws/occurrence/facets?facets=data_provider_uid&flimit=1000"

DR_INFO_URL = "https://collections.ala.org.au/ws/dataResource/"

DP_INFO_URL = "https://collections.ala.org.au/ws/dataProvider/"
BAD_DOI_URL = "http://doi.org/doi.org/"
DOI_URL = "http://doi.org/doi:"
SHORT_DOI_URL = "http://doi.org/"


def main(log_level=logging.INFO):

    # set up logger
    logging.basicConfig(filename='gbif_publication_data.log',level=log_level)

    retrieve_gbif_registry_keys()

    # load data resources with keys
    df = pd.read_csv('gbif_registry_keys.csv')

    publications = []

    # iterate through data resources
    for i,r in df.iterrows():
        # gbif key exists
        if not pd.isna(r['gbifRegistryKey']):
            key = r['gbifRegistryKey']

        # try and use doi to retrieve key
        elif pd.isna(r['gbifRegistryKey']) and not pd.isna(r['doi']):
            key = get_key_from_doi(r['doi'])

        # can't do anything so skip
        else:
            continue

        results = registry_data_from_key(key)

        for r in results:
            data = publication_data(r)
            publications.append(data)

    df = pd.DataFrame(publications)
    df.set_index('id', inplace=True)
    df.fillna('',inplace=True)
    df.drop_duplicates(inplace = True)
    df.to_csv('publications_from_gbif.csv')


def get_key_from_doi(doi):
    # if dodgy doi url is in string e.g. http://doi.org/doi.org/10.15468/pgtpoq
    if BAD_DOI_URL in doi:
        url = DOI_URL + doi.split('/')[-2] + '/' + doi.split('/')[-1]
    # if doi resolver is already in string e.g. http://doi.org/doi:10.15468/eplomk
    elif DOI_URL in doi:
        url = doi
    # if just 'doi' is in string e.g. doi:10.15468/bxxmis
    elif 'doi' in doi:
        url = SHORT_DOI_URL + doi
    # if just raw doi e.g. 10.15468/rtnb4m
    else:
        url = DOI_URL + doi

    # make request to doi url and use redirect url to deduce key
    resp = requests.get(url)
    key = resp.url.split('/')[-1]
    is_gbif = resp.url.split('/')[2] == 'www.gbif.org'
    if not is_gbif:
        # try gbif search on the last part of the doi
        key = last_ditch_gbif_search(doi)

    return key

def last_ditch_gbif_search(doi):
    # last part of doi
    doi_str = doi.split('/')[-1]
    url = DATASET_SEARCH_URL + doi_str
    resp = requests.get(url)
    if resp.json()['count'] == 1:
        return resp.json()['results'][0]['key']
    # if more than one result is returned it will need to be manually checked
    return ''

def registry_data_from_key(key):
    url = GBIF_URL_PREFIX + key
    resp = requests.get(url)
    results = resp.json()['results']
    logging.info('Key %s returned %d results',key,len(results))
    return results

def publication_data(result):
    id = result['id']
    date = result['created']
    data = {'id':id, 'created':date}

    doi = publication_doi(result)
    if doi:
        data['doi'] = doi
    else:
        data['first_author'] = format_author(result['authors']) if 'authors' in result.keys() else ""
        data['source'] = result['source'] if 'source' in result.keys() else ''
        data['title'] = result['title'] if 'title' in result.keys() else ''
        data['year'] = int(result['year']) if 'year' in result.keys() else ''
        data['websites'] = format_websites(result['websites']) if 'websites' in result.keys() else ''

    return data


def publication_doi(pub):
    try:
        doi = pub['identifiers']['doi']
        return True
    except KeyError:
        return False


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

    # retrieve gbif citation key and/or doi
    for dr in drs:
        try:
            url = DR_INFO_URL + dr
            resp = requests.get(url)
            data = {'dataResource': dr}
            if 'gbifRegistryKey' in resp.json().keys():
                data['gbifRegistryKey'] = resp.json()['gbifRegistryKey']
            if 'gbifDoi' in resp.json().keys():
                data['gbifDoi'] = resp.json()['gbifDoi']
            if 'isShareableWithGBIF' in resp.json().keys():
                data['isShareableWithGBIF'] = resp.json()['isShareableWithGBIF']
            if 'doi' in resp.json().keys():
                data['doi'] = resp.json()['doi']
            keys.append(data)
        except (KeyError,json.decoder.JSONDecodeError):
            print('no key found')
    # write keys to csv for later verification
    df = pd.DataFrame(keys)
    df.to_csv('gbif_registry_keys.csv', index = False)
    return keys

if __name__ == '__main__':
    main()
