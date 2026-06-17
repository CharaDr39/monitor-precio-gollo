import os
import re
import smtplib
import requests
from bs4 import BeautifulSoup
from email.message import EmailMessage

PRODUCT_URL = "https://www.gollo.com/monitor-gaming-acer-ips-27-fhd-negro-vg270p6bip-1004030007/p"
LAST_PRICE_FILE = "last_price.txt"
TARGET_MIN_PRICE = 40000
TARGET_MAX_PRICE = 60000


def clean_price(value):
    """
    Convierte precios tipo:
    ₡79.900
    79,900
    79900.0
    a entero: 79900
    """
    if value is None:
        return None

    text = str(value)

    # Si viene como 79900.0
    if re.fullmatch(r"\d+(\.\d+)?", text):
        return int(float(text))

    # Si viene como ₡79.900 o 79,900
    text = text.replace("₡", "").replace("CRC", "").strip()
    text = text.replace(".", "").replace(",", "")

    numbers = re.findall(r"\d+", text)

    if not numbers:
        return None

    return int(numbers[0])


def get_price_from_page():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(PRODUCT_URL, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    page_text = soup.get_text(" ", strip=True)

    product_name = 'Monitor Gaming Acer IPS 27" FHD Negro VG270P6BIP'

    start_index = page_text.find(product_name)

    if start_index == -1:
        raise ValueError("No encontré el nombre del producto en la página.")

    # Tomamos solo una parte cercana al producto, no toda la página
    product_section = page_text[start_index:start_index + 2000]

    matches = re.findall(r"₡\s?[\d.,]+", product_section)

    prices = []

    for match in matches:
        price = clean_price(match)

        # Evita cuotas pequeñas tipo ₡7.492
        # y evita montos raros demasiado bajos
        if price and 40000 <= price <= 200000:
            prices.append(price)

    print("Precios encontrados cerca del producto:")
    print(prices)

    if not prices:
        raise ValueError("No encontré precios válidos cerca del producto.")

    # El precio actual normalmente aparece antes que el precio tachado
    return prices[0]


def format_crc(price):
    return f"₡{price:,.0f}".replace(",", ".")


def send_email(old_price, new_price):
    email_from = os.environ["EMAIL_FROM"]
    email_to = os.environ["EMAIL_TO"]
    email_password = os.environ["EMAIL_PASSWORD"]

    if new_price < old_price:
        movement = "bajó"
    elif new_price > old_price:
        movement = "subió"
    else:
        movement = "cambió"

    difference = new_price - old_price

    is_target_price = TARGET_MIN_PRICE <= new_price <= TARGET_MAX_PRICE

    msg = EmailMessage()

    if is_target_price:
        msg["Subject"] = f"🚨 COMPRALO YA: el monitor está en {format_crc(new_price)} 🚨"
        body = f"""🚨 PRECIO OBJETIVO DETECTADO 🚨

El monitor Acer en Gollo está dentro del rango que querías.

Precio anterior: {format_crc(old_price)}
Precio nuevo: {format_crc(new_price)}
Diferencia: {format_crc(difference)}

Rango objetivo:
{format_crc(TARGET_MIN_PRICE)} - {format_crc(TARGET_MAX_PRICE)}

COMPRALO YA ANTES DE QUE GOLLO SE ACUERDE DE QUE EXISTE LA INFLACIÓN.

Link:
{PRODUCT_URL}
"""
    else:
        msg["Subject"] = f"El monitor {movement}: {format_crc(new_price)}"
        body = f"""El precio del monitor Acer en Gollo cambió.

Precio anterior: {format_crc(old_price)}
Precio nuevo: {format_crc(new_price)}
Diferencia: {format_crc(difference)}

Todavía no está en el rango objetivo de {format_crc(TARGET_MIN_PRICE)} a {format_crc(TARGET_MAX_PRICE)}.

Link:
{PRODUCT_URL}
"""

    msg["From"] = email_from
    msg["To"] = email_to
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(email_from, email_password)
        smtp.send_message(msg)


def read_last_price():
    with open(LAST_PRICE_FILE, "r", encoding="utf-8") as file:
        return int(file.read().strip())


def save_last_price(price):
    with open(LAST_PRICE_FILE, "w", encoding="utf-8") as file:
        file.write(str(price))


def main():
    old_price = read_last_price()
    new_price = get_price_from_page()

    print(f"Precio anterior: ₡{old_price:,}")
    print(f"Precio actual: ₡{new_price:,}")

    if new_price != old_price:
        print("El precio cambió. Enviando correo...")
        send_email(old_price, new_price)
        save_last_price(new_price)
        print("Correo enviado y precio actualizado.")
    else:
        print("El precio no cambió. El monitor sigue jugando con tus emociones, pero no hoy.")


if __name__ == "__main__":
    main()
