from __future__ import annotations

import re

from .helpers import combinar_fecha_hora, convertir_float, limpiar_texto


class Validaciones:
    @staticmethod
    def validar_campos_obligatorios(campos):
        for nombre, valor in campos.items():
            if not limpiar_texto(valor):
                return False, f"El campo '{nombre}' es obligatorio."
        return True, ""

    @staticmethod
    def validar_documento_unico(documento, registros, campo="documento", ignorar=None):
        documento = limpiar_texto(documento)
        ignorar = limpiar_texto(ignorar)
        for registro in registros:
            valor_actual = limpiar_texto(registro.get(campo))
            if valor_actual == documento and valor_actual != ignorar:
                return False, "Ya existe un registro con ese documento."
        return True, ""

    @staticmethod
    def validar_username_unico(username, registros, ignorar=None):
        username = limpiar_texto(username).lower()
        ignorar = limpiar_texto(ignorar).lower()
        for registro in registros:
            actual = limpiar_texto(registro.get("username")).lower()
            if actual == username and actual != ignorar:
                return False, "El nombre de usuario ya existe."
        return True, ""

    @staticmethod
    def validar_email(correo):
        correo = limpiar_texto(correo)
        if not correo:
            return True, ""
        patron = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        if re.match(patron, correo):
            return True, ""
        return False, "El correo electrónico no tiene un formato válido."

    @staticmethod
    def validar_monto_positivo(valor, etiqueta="valor"):
        try:
            monto = convertir_float(valor)
        except ValueError:
            return False, f"El campo '{etiqueta}' debe ser numérico."

        if monto <= 0:
            return False, f"El campo '{etiqueta}' debe ser mayor que cero."
        return True, ""

    @staticmethod
    def validar_fecha_hora(fecha, hora):
        try:
            combinar_fecha_hora(fecha, hora)
            return True, ""
        except ValueError:
            return False, "La fecha u hora no tienen un formato válido."

    @staticmethod
    def validar_login(username, password):
        return Validaciones.validar_campos_obligatorios(
            {"usuario": username, "contraseña": password}
        )
