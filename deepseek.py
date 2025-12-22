import requests

def ds_credits(ds_api_key):
    """
    Consulta el balance actual del usuario en DeepSeek.
    """
    url = "https://api.deepseek.com/user/balance"
    headers = {
        "Authorization": f"Bearer {ds_api_key}",
        "Content-Type": "application/json",
    }

    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    balance_info = data
    if balance_info:
        return f"Deepseek_usd_left: {balance_info.get('balance_infos', [])[0].get('total_balance')} USD"
    else:
        return None