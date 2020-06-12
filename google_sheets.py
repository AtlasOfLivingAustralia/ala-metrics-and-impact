from apiclient.http import MediaFileUpload
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build


def write_to_google_sheet():

    file_metadata = {
    'name': 'Zotero_Python',
    'mimeType': 'application/vnd.google-apps.spreadsheet'
    }

    # use google service account to create google sheet
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    creds = Credentials.from_json_keyfile_name('client_secret.json', scope)

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


def callback(request_id, response, exception):
    if exception:
        # Handle error
        print(exception)
    else:
        print("Permission Id: %s" % response.get('id'))

if __name__ == '__main__':
    write_to_google_sheet()
