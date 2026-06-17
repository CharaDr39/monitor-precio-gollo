import os
import re
import smtplib
import requests
from bs4 import BeautifulSoup
from email.message import EmailMessage

PRODUCT_URL = "https://www.gollo.com/monitor-gaming-acer-ips-27-fhd-negro-vg270p6bip-1004030007/p"
LAST_PRICE_FILE = "last_price.txt"


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

    # Busca precios con símbolo ₡
    matches = re.findall(r"₡\s?[\d.,]+", page_text)

    prices = []

    for match in matches:
        price = clean_price(match)

        # Filtro para evitar precios absurdos tipo cuotas muy pequeñas
        if price and price >= 10000:
            prices.append(price)

    if not prices:
        raise ValueError("No encontré precios válidos en la página.")

    # Usamos el menor precio razonable porque normalmente es el precio de oferta
    return min(prices)


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

    msg = EmailMessage()
    msg["Subject"] = f"El monitor {movement}: ₡{new_price:,}"
    msg["From"] = email_from
    msg["To"] = email_to

    msg.set_content(
        f"""El precio del monitor Acer en Gollo cambió.

Precio anterior: ₡{old_price:,}
Precio nuevo: ₡{new_price:,}
Diferencia: ₡{difference:,}

Link:
{PRODUCT_URL}
"""
    )

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
