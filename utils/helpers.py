from __future__ import annotations

from datetime import datetime
from uuid import uuid4


FORMATO_FECHA = "%Y-%m-%d"
FORMATO_HORA = "%H:%M"
FORMATO_FECHA_HORA = "%Y-%m-%d %H:%M:%S"
FORMATOS_LEGACY_CITA = ("%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M")


def limpiar_texto(valor):
    return str(valor or "").strip()


def generar_id(prefijo):
    sello = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefijo}-{sello}-{uuid4().hex[:6].upper()}"


def fecha_actual():
    return datetime.now().strftime(FORMATO_FECHA)


def hora_actual():
    return datetime.now().strftime(FORMATO_HORA)


def fecha_hora_actual():
    return datetime.now().strftime(FORMATO_FECHA_HORA)


def dividir_fecha_hora(valor_fecha, valor_hora=""):
    fecha = limpiar_texto(valor_fecha)
    hora = limpiar_texto(valor_hora)

    if fecha and hora:
        return fecha, hora

    for formato in FORMATOS_LEGACY_CITA:
        try:
            fecha_hora = datetime.strptime(fecha, formato)
            return fecha_hora.strftime(FORMATO_FECHA), fecha_hora.strftime(FORMATO_HORA)
        except ValueError:
            continue

    if " " in fecha and not hora:
        partes = fecha.split()
        if len(partes) >= 2:
            return limpiar_texto(partes[0]), limpiar_texto(partes[1][:5])

    return fecha, hora


def combinar_fecha_hora(fecha, hora):
    fecha = limpiar_texto(fecha)
    hora = limpiar_texto(hora)
    return datetime.strptime(f"{fecha} {hora}", f"{FORMATO_FECHA} {FORMATO_HORA}")


def convertir_float(valor):
    return float(str(valor).replace(",", "."))
