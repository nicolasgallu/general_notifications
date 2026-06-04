from dotenv import load_dotenv
from telegram_notify import send_message
from deepseek import ds_credits
from mercadolibre import meli_metrics
from scrapfly import advice_payment_scrapfly
import os

load_dotenv()

ds_api_key = os.getenv("DEEPSEEK_API_KEY")
meli_metrics_url = os.getenv("METRICS_MELI_URL")
telegram_chat_ids_customer = os.getenv("TELEGRAM_CHAT_IDS_CUSTOMER").split(",")
telegram_chat_ids_internal = os.getenv("TELEGRAM_CHAT_IDS_INTERNAL").split(",")
url_wh = os.getenv("URL_WH")


scrapfly_key = os.getenv("SCRAPFLY_TOKEN")
whapi_token = os.getenv("WHAPI_TOKEN")
wpp_phone = os.getenv("WPP_CONTACTS")


if __name__ == "__main__":
    #DeepSeek Notifications
    deepseek_data = ds_credits(ds_api_key)
    print(deepseek_data)
    send_message(url_wh, deepseek_data, telegram_chat_ids_internal)
    #Mercadolibre Notifications
    #Pending: Diseñar un modelo que soporte varios clientes y que lea desde DB no de Sheets.
    meli_data = meli_metrics()
    send_message(url_wh, meli_data, telegram_chat_ids_customer+telegram_chat_ids_internal)
    advice_payment_scrapfly(scrapfly_key, whapi_token, wpp_phone)
