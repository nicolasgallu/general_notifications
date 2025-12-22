from dotenv import load_dotenv
from telegram_notify import send_message
from deepseek import ds_credits
from mercadolibre import meli_metrics
import os

load_dotenv()

#diferenciar entre public y private chats, para determinar que comunicaciones van para clientes y cuales son de caracter interno

##GBQ ACCESS
google_service_account = {
'type': os.getenv("type"),
'project_id': os.getenv("project_id"),
'private_key_id': os.getenv("private_key_id"),
'private_key': os.getenv("private_key").replace('\\n', '\n'),
'client_email': os.getenv("client_email"),
'client_id': os.getenv("client_id"),
'auth_uri': os.getenv("auth_uri"),
'token_uri': os.getenv("token_uri"),
'auth_provider_x509_cert_url': os.getenv("auth_provider_x509_cert_url"),
'client_x509_cert_url': os.getenv("client_x509_cert_url"),
'universe_domain': os.getenv("universe_domain")
}

ds_api_key = os.getenv("DEEPSEEK_API_KEY")
meli_metrics_url = os.getenv("METRICS_MELI_URL")
telegram_chat_ids_customer = os.getenv("TELEGRAM_CHAT_IDS_CUSTOMER").split(",")
telegram_chat_ids_internal = os.getenv("TELEGRAM_CHAT_IDS_INTERNAL").split(",")
url_wh = os.getenv("URL_WH")


if __name__ == "__main__":
    #DeepSeek Notifications
    deepseek_data = ds_credits(ds_api_key)
    send_message(url_wh, deepseek_data, telegram_chat_ids_internal)
    #Mercadolibre Notifications
    #Pending: Diseñar un modelo que soporte varios clientes y que lea desde DB no de Sheets.
    meli_data = meli_metrics(google_service_account, meli_metrics_url)
    send_message(url_wh, meli_data, telegram_chat_ids_customer+telegram_chat_ids_internal)