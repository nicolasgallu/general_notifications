import requests
from datetime import datetime, timedelta

def advice_payment_scrapfly(scrapfly_key, whapi_token, whapi_phone):
    url = f"https://api.scrapfly.io/account?key={scrapfly_key}"
    response = requests.get(url)
    
    if response.status_code != 200:
        return "Error al conectar con Scrapfly"

    # Extraer datos de Scrapfly
    sub_data = response.json().get("subscription", {})
    period = sub_data.get("period", {})
    end_at = period.get("end")

    fecha_fin = datetime.fromisoformat(end_at.replace('Z', '')).date()
    hoy = datetime.now().date()
    manana = hoy + timedelta(days=1)

    # Lógica de comparación
    if fecha_fin == hoy or fecha_fin == manana:
        mensaje = (
            f"Hola Giuli, soy Nicolas. Te recuerdo fondear la cuenta de Scrapfly con la tarjeta Ualá, "
            f"ya que la suscripción vence el día {fecha_fin}. Al terminar, avísale a Matias para que "
            f"podamos actualizar las credenciales. ¡Gracias!"
        )
        # Llamada a Whapi (Reutilizando la lógica anterior)
        return enviar_mensaje_whapi(whapi_token, whapi_phone, mensaje)
    else:
        return None

def enviar_mensaje_whapi(token, telefono, mensaje):
    url = "https://gate.whapi.cloud/messages/text"
    payload = {
        "to": f"{telefono}",
        "body": mensaje
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {token}"
    }
    
    res = requests.post(url, json=payload, headers=headers)
    return res.json()
