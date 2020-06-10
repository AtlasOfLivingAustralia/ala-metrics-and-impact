import requests
import pandas as pd
import config
import zotero
from apiclient.http import MediaFileUpload
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from datetime import date

API_KEY = config.API_KEY
PLUMX_URL = "https://api.elsevier.com/analytics/plumx/doi/"
ALTMETRIC_URL = "https://api.altmetric.com/v1/doi/"
SCOPUS_CITATION_URL = "https://api.elsevier.com/content/search/scopus?query=DOI("
SCOPUS_JOURNAL_URL = "https://api.elsevier.com/content/serial/title/issn/"
IN_PATH = 'zotero_data.csv'
OUTPATH = 'all_data.csv'

def main():
    # read in zotero data
    df = read_dois(IN_PATH)

    # loop through dois and retrieve metrics for each
    for i,r in df.iterrows():

        doi = r['DOI']
        if doi != '':
            plumx_data = retrieve_plumx_data(doi)
            altmetric_data = retrieve_altmetric_data(doi)
            scopus_cited_data = retrieve_scopus_citation_data(doi)
            issn = scopus_cited_data['ISSN [Scopus]']
            scopus_journal_data = retrieve_scopus_journal_data(issn)

            # join metrics together in row
            row = {'DOI': doi, **plumx_data, **altmetric_data, **scopus_cited_data, **scopus_journal_data}

            #
            scores_df = scores_df.append(pd.Series(row), ignore_index=True)

    # set index of zotero and scores dataframes for easier joining
    df.set_index('DOI',inplace = True)
    scores_df.set_index('DOI',inplace = True)

    # join the dataframes and write to csv
    all_data = pd.concat([scores_df,df],axis = 1)
    write_metrics(all_data, OUTPATH)

    write_to_google_sheet()


def read_dois(path):
    return pd.read_csv(path)

def write_metrics(df, path):
    df.to_csv(path, index=False)
    return


def retrieve_plumx_data(doi):
    url = PLUMX_URL + str(doi) + '?apiKey=' + API_KEY
    resp = requests.get(url)
    if resp.status_code != 200:
        print(url)
        print("No response from plumx for ", doi)
        return {}
    try:
        data = resp.json()['count_categories']
    except KeyError:
        return {}
    stats = {}

    for i in data:
        if i['name'] == 'citation':
            stats['Citations [PlumX]'] = i['total']
        elif i['name'] == 'mention':
            for j in i['count_types']:
                if j['name'] == 'ALL_BLOG_COUNT':
                    stats['Blogs [PlumX]'] = j['total']
                elif j['name'] == 'NEWS_COUNT':
                    stats['News [PlumX]'] = j['total']
        elif i['name'] == 'socialMedia':
            for j in i['count_types']:
                if j['name'] == 'TWEET_COUNT':
                    stats['Tweets [PlumX]'] = j['total']
                elif j['name'] == 'FACEBOOK_COUNT':
                    stats['Facebook [PlumX]'] = j['total']

    return stats


def retrieve_altmetric_data(doi):
    url = ALTMETRIC_URL + str(doi)
    resp = requests.get(url)
    if resp.status_code != 200:
        print(url)
        print("No response from altmetric for ",doi)
        return {}
    print("altmetric working")
    data = resp.json()
    stats = {}
    stats['Score [Altmetric]'] = data['score']
    stats['News [Altmetric]'] = data['cited_by_msm_count'] if 'cited_by_msm_count' in data.keys() else 0
    stats['Facebook [Altmetric]'] = data['cited_by_fbwalls_count'] if 'cited_by_fbwalls_count' in data.keys() else 0
    stats['Blogs [Altmetric]'] = data['cited_by_feeds_count'] if 'cited_by_feeds_count' in data.keys() else 0
    stats['Google+ [Altmetric]'] = data['cited_by_gplus_count'] if 'cited_by_gplus_count' in data.keys() else 0
    stats['Twitter [Altmetric]'] = data['cited_by_tweeters_count'] if 'cited_by_tweeters_count' in data.keys() else 0
    stats['Subjects [Altmetric]'] = str(data['subjects']) if 'subjects' in data.keys() else ''

    # should is_oa and cited_by_posts_count also be included here?
    return stats

def retrieve_scopus_citation_data(doi):
    url = SCOPUS_CITATION_URL + str(doi) + ")&apiKey=" + API_KEY
    resp = requests.get(url)
    if resp.status_code != 200:
        print(url)
        error("No valid result")
        return {}
    data = resp.json()['search-results']['entry'][0]
    stats = {}
    stats['Journal [Scopus]'] = data['prism:publicationName'] if 'prism:publicationName' in data.keys() else ''
    stats['Cite count [Scopus]'] = data['citedby-count'] if 'citedby-count' in data.keys() else 0
    stats['eISSN [Scopus]'] = data['prism:eIssn'] if 'prism:eIssn' in data.keys() else ''
    stats['ISSN [Scopus]'] = data['prism:issn'] if 'prism:issn' in data.keys() else ''
    return stats

def retrieve_scopus_journal_data(issn):
    if issn == "":
        return {}
    url = SCOPUS_JOURNAL_URL + str(issn) + '?apiKey=' + API_KEY
    resp = requests.get(url)
    data = resp.json()
    try:
        sjr = data["serial-metadata-response"]["entry"][0]["SJRList"]["SJR"][0]["$"]
    except:
        sjr = ''
    try:
        snip = data["serial-metadata-response"]["entry"][0]["SNIPList"]["SNIP"][0]["$"]
    except:
        snip = ''
    return {'SJR': sjr, 'SNIP': snip}


def callback(request_id, response, exception):
    if exception:
        # Handle error
        print(exception)
    else:
        print("Permission Id: %s" % response.get('id'))


def write_to_google_sheet():

    file_metadata = {
    'name': 'Zotero_Python',
    'mimeType': 'application/vnd.google-apps.spreadsheet'
    }

    # use google service account to create google sheet
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)

    drive_service = build('drive', 'v3', credentials=creds)
    media = MediaFileUpload('all_data.csv',
                            mimetype='text/csv',
                            resumable=True)

    file = drive_service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()

    # retrieve id and use to give permission to analytics account
    id = file.get('id')
    print(id
    )

    batch = drive_service.new_batch_http_request(callback=callback)
    user_permission = {
    'type': 'user',
    'role': 'writer',
    'emailAddress': 'analytics@ala.org.au'
    }
    batch.add(drive_service.permissions().create(
    fileId=id,
    body=user_permission,
    fields='id'
    ))

    batch.execute()

if __name__ == '__main__':
    main()
