# Gollo Price Tracker 🇨🇷

Bot simple hecho con **Python + GitHub Actions** para revisar automáticamente el precio de un producto en **Gollo Costa Rica** y mandar un correo cuando el precio cambia.

Nació porque un monitor pasó de ₡50.905 a casi ₡90.000, y claramente eso no podía quedar sin vigilancia automatizada. Si las tiendas van a jugar con los precios, al menos que GitHub nos avise mientras dormimos.

---

## ¿Qué hace?

Este proyecto:

1. Entra a la página de un producto de Gollo.
2. Lee el precio actual.
3. Lo compara contra el último precio guardado en `last_price.txt`.
4. Si el precio cambió:

   * manda un correo,
   * dice si subió o bajó,
   * actualiza `last_price.txt` con el nuevo precio.
5. Si el precio sigue igual:

   * no manda correo,
   * solo deja el resultado en los logs del Action.

---

## Pensado para Costa Rica

Este proyecto está pensado para páginas de tiendas en Costa Rica que muestran precios en colones, especialmente Gollo.

Ejemplo de precio esperado:

```txt
₡89.905
```

Internamente el bot guarda los precios como número limpio:

```txt
89905
```

Sin símbolo de colón, sin puntos y sin comas.

---

## Archivos principales

```txt
golllo-price-tracker/
├─ check_price.py
├─ last_price.txt
├─ requirements.txt
├─ README.md
└─ .github/
   └─ workflows/
      └─ price-check.yml
```

---

## Requisitos

Para usarlo necesitás:

* Una cuenta de GitHub.
* Un repo con GitHub Actions activado.
* Una cuenta de Gmail.
* Una contraseña de aplicación de Google.
* Tres secrets configurados en GitHub.

No necesitás tener un servidor encendido. GitHub Actions corre el script automáticamente en una máquina temporal.

---

## Instalación rápida

### 1. Hacer fork o clonar el repo

Podés hacer fork del repo o clonarlo en tu compu:

```bash
git clone URL_DEL_REPO
```

Luego entrás a la carpeta:

```bash
cd NOMBRE_DEL_REPO
```

---

## 2. Cambiar el URL del producto

Abrí el archivo:

```txt
check_price.py
```

Buscá esta línea:

```python
PRODUCT_URL = "https://www.gollo.com/monitor-gaming-acer-ips-27-fhd-negro-vg270p6bip-1004030007/p"
```

Cambiá ese link por el producto de Gollo que querés monitorear.

Ejemplo:

```python
PRODUCT_URL = "https://www.gollo.com/tu-producto-aqui/p"
```

---

## 3. Cambiar el nombre del producto si aplica

En algunas versiones del script puede existir una línea parecida a esta:

```python
product_name = 'Monitor Gaming Acer IPS 27" FHD Negro VG270P6BIP'
```

Si tu script la tiene, cambiá ese texto por el nombre exacto o casi exacto del producto que aparece en Gollo.

Ejemplo:

```python
product_name = 'Laptop Lenovo IdeaPad 15.6"'
```

Esto ayuda a que el script busque precios cerca del producto correcto y no agarre cuotas, seguros, reparaciones o cualquier otro número raro que la página tenga tirado por ahí como confeti financiero.

---

## 4. Cambiar el precio inicial

Abrí el archivo:

```txt
last_price.txt
```

Poné el precio actual del producto, pero limpio.

Ejemplo: si en Gollo aparece:

```txt
₡89.905
```

En `last_price.txt` tenés que poner:

```txt
89905
```

No pongás:

```txt
₡89.905
```

Tampoco pongás:

```txt
89,905
```

Solo el número:

```txt
89905
```

Ese archivo es la memoria del bot. Sin eso, el pobre script no sabe si el precio cambió o si simplemente está viendo el mismo desastre de ayer.

---

## 5. Configurar los secrets

En GitHub, entrá al repo y andá a:

```txt
Settings → Secrets and variables → Actions → New repository secret
```

Tenés que crear estos tres secrets exactamente con estos nombres:

```txt
EMAIL_FROM
EMAIL_TO
EMAIL_PASSWORD
```

---

### EMAIL_FROM

Correo que enviará la alerta.

Ejemplo:

```txt
tu_correo@gmail.com
```

---

### EMAIL_TO

Correo que recibirá la alerta.

Puede ser el mismo correo de `EMAIL_FROM`.

Ejemplo:

```txt
tu_correo@gmail.com
```

Sí, te podés mandar correos a vos mismo. Ridículo, pero funciona.

---

### EMAIL_PASSWORD

Esta NO es tu contraseña normal de Gmail.

Tiene que ser una **contraseña de aplicación** de Google.

Google normalmente la muestra como una clave de 16 caracteres, algo parecido a esto:

```txt
abcd efgh ijkl mnop
```

Podés pegarla en GitHub con o sin espacios, aunque normalmente es más limpio ponerla junta:

```txt
abcdefghijklmnop
```

---

## 6. Crear una contraseña de aplicación en Google

Para usar Gmail con este script:

1. Entrá a tu cuenta de Google.
2. Andá a Seguridad.
3. Activá Verificación en 2 pasos si no la tenés activa.
4. Buscá Contraseñas de aplicaciones.
5. Creá una nueva.
6. Copiá la clave de 16 caracteres.
7. Pegala en el secret `EMAIL_PASSWORD`.

No pongás esa contraseña en archivos del repo. Menos si el repo es público. Eso sería básicamente regalarle tu correo a internet con moño.

---

## 7. Workflow de GitHub Actions

El archivo del workflow está en:

```txt
.github/workflows/price-check.yml
```

El workflow corre automáticamente con esta parte:

```yaml
on:
  schedule:
    - cron: "17 12 * * *"
  workflow_dispatch:
```

Eso significa:

* `schedule`: corre automáticamente una vez al día.
* `workflow_dispatch`: permite correrlo manualmente desde la pestaña Actions.

El horario del cron está en UTC. Por ejemplo:

```yaml
cron: "17 12 * * *"
```

Corre a las 12:17 UTC, que en Costa Rica corresponde a las 6:17 a.m.

---

## 8. Ejecutarlo manualmente

Para probarlo:

1. Entrá al repo en GitHub.
2. Andá a la pestaña Actions.
3. Elegí el workflow llamado algo como:

```txt
Revisar precio monitor Gollo
```

4. Tocá:

```txt
Run workflow
```

5. Esperá a que termine.

Si el precio cambió, te manda correo.

Si el precio sigue igual, no manda correo y solo lo muestra en los logs.

---

## 9. Ejemplo de correo

Si el precio baja:

```txt
Asunto: El monitor bajó: ₡50,905

El precio del monitor Acer en Gollo cambió.

Precio anterior: ₡89,905
Precio nuevo: ₡50,905
Diferencia: ₡-39,000

Link:
https://www.gollo.com/...
```

Si el precio sube:

```txt
Asunto: El monitor subió: ₡97,500

El precio del monitor Acer en Gollo cambió.

Precio anterior: ₡89,905
Precio nuevo: ₡97,500
Diferencia: ₡7,595

Link:
https://www.gollo.com/...
```

---

## 10. Dependencias

El archivo:

```txt
requirements.txt
```

usa:

```txt
requests
beautifulsoup4
```

`requests` descarga la página.

`beautifulsoup4` ayuda a leer el HTML.

Básicamente uno trae el desastre y el otro intenta entenderlo. Trabajo en equipo, pero con más etiquetas `<div>` de las necesarias.

---

## 11. Cosas que probablemente vas a cambiar

Si querés usar este proyecto con otro producto, normalmente solo cambiás esto:

### En `check_price.py`

```python
PRODUCT_URL = "URL_DEL_PRODUCTO"
```

Y si tu versión del script tiene `product_name`:

```python
product_name = "NOMBRE_DEL_PRODUCTO"
```

### En `last_price.txt`

```txt
PRECIO_ACTUAL_LIMPIO
```

Ejemplo:

```txt
89905
```

### En GitHub Secrets

```txt
EMAIL_FROM
EMAIL_TO
EMAIL_PASSWORD
```

---

## 12. Notas importantes

Este bot depende de que la página de Gollo mantenga una estructura más o menos parecida.

Si Gollo cambia la página, el script puede fallar o leer un precio incorrecto.

Si eso pasa, revisá los logs del Action. El script imprime los precios encontrados cerca del producto para ayudar a detectar si está agarrando el número correcto o si está confundiendo el precio real con una cuota, descuento, seguro o alguna otra maravilla del comercio moderno.

---

## 13. Seguridad

No subás contraseñas al repo.

No pongás tu correo ni tu contraseña de aplicación directamente en `check_price.py`.

Usá GitHub Secrets.

Esto es especialmente importante si el repo es público.

Los secrets deben configurarse desde GitHub, no desde el código.

---

## 14. ¿Puedo usarlo con otras tiendas?

Sí, pero puede requerir cambios.

Este script está hecho pensando en Gollo Costa Rica y precios en colones.

Otras tiendas pueden tener HTML diferente, precios cargados por JavaScript o estructuras más complicadas.

Si la tienda carga el precio después con JavaScript, `requests` puede no verlo directamente y habría que usar otra estrategia.

---

## 15. ¿Por qué existe esto?

Porque revisar manualmente si un producto bajó de precio es una pérdida de tiempo.

Y porque si un monitor puede subir de ₡50.905 a ₡89.905, entonces claramente merece vigilancia automatizada.
