import gspread
from oauth2client.service_account import ServiceAccountCredentials


def meli_metrics(credentials,meli_metrics_url):

    # 1. Setup credentials and authorize
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials,scopes=scope)
    client = gspread.authorize(creds)

    # 2. Open the sheet by URL
    spreadsheet = client.open_by_url(meli_metrics_url)
    sheet = spreadsheet.worksheet("yesterday_performance")  # Use the exact tab name here

    # 3. Read the 2nd row (A to F)
    data_row=sheet.row_values(2)
    # 4. Separate variables
    created_at = data_row[0]
    preguntas = data_row[1]
    respondidas = data_row[2]
    no_respondidas = data_row[3]
    share_respondidas = data_row[4]
    # 4. Separate variables
    meli_metrics = (f"MercadoLibre Yesterday Metrics\n-preguntas: {preguntas}\n-respondidas: {respondidas}\n-no_respondidas: {no_respondidas}\n-share_respondidas: {share_respondidas}")
    return meli_metrics
    
