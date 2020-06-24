from apiclient.http import MediaFileUpload
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import config
import gspread
import sys
import pandas as pd
import gspread_pandas

def write_to_sheet(outfile, credentials_path):
    df = pd.read_csv(outfile)
    spread = gspread_pandas.Spread(config.SPREADSHEET_ID,
    config = gspread_pandas.conf.get_config(file_name = credentials_path))
    spread.df_to_sheet(df, index=False, sheet='Sheet1', start='A1', replace=True)

    return

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Please provide the name of a csv file to read from, and the path to your credentials file")
        exit(1)
    write_to_sheet(sys.argv[1], sys.argv[2])
