from __future__ import annotations

from utils.helpers import convertir_float, fecha_actual, generar_id, limpiar_texto


class Factura:
    def __init__(
        self,
        documento_paciente,
        concepto,
        valor_total,
        fecha=None,
        estado_pago="Pendiente",
        id_factura=None,
        nombre_paciente="",
    ):
        self.__id_factura = limpiar_texto(id_factura) or generar_id("FAC")
        self.__documento_paciente = limpiar_texto(documento_paciente)
        self.__nombre_paciente = limpiar_texto(nombre_paciente)
        self.__fecha = limpiar_texto(fecha) or fecha_actual()
        self.__concepto = limpiar_texto(concepto)
        self.__valor_total = convertir_float(valor_total)
        self.__estado_pago = limpiar_texto(estado_pago) or "Pendiente"

    @property
    def id_factura(self):
        return self.__id_factura

    @property
    def documento_paciente(self):
        return self.__documento_paciente

    @property
    def nombre_paciente(self):
        return self.__nombre_paciente

    @property
    def fecha(self):
        return self.__fecha

    @property
    def concepto(self):
        return self.__concepto

    @property
    def valor_total(self):
        return self.__valor_total

    @property
    def estado_pago(self):
        return self.__estado_pago

    @estado_pago.setter
    def estado_pago(self, valor):
        self.__estado_pago = limpiar_texto(valor)

    def to_dict(self):
        return {
            "id_factura": self.__id_factura,
            "documento_paciente": self.__documento_paciente,
            "nombre_paciente": self.__nombre_paciente,
            "fecha": self.__fecha,
            "concepto": self.__concepto,
            "valor_total": self.__valor_total,
            "estado_pago": self.__estado_pago,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            documento_paciente=data.get("documento_paciente", ""),
            nombre_paciente=data.get("nombre_paciente", ""),
            fecha=data.get("fecha"),
            concepto=data.get("concepto", ""),
            valor_total=data.get("valor_total", 0),
            estado_pago=data.get("estado_pago", "Pendiente"),
            id_factura=data.get("id_factura"),
        )
