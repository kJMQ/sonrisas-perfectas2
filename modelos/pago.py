from __future__ import annotations

from utils.helpers import convertir_float, fecha_actual, generar_id, limpiar_texto


class Pago:
    def __init__(
        self,
        id_factura,
        valor_pagado,
        metodo_pago,
        fecha=None,
        id_pago=None,
        documento_paciente="",
    ):
        self.__id_pago = limpiar_texto(id_pago) or generar_id("PAG")
        self.__id_factura = limpiar_texto(id_factura)
        self.__documento_paciente = limpiar_texto(documento_paciente)
        self.__fecha = limpiar_texto(fecha) or fecha_actual()
        self.__valor_pagado = convertir_float(valor_pagado)
        self.__metodo_pago = limpiar_texto(metodo_pago)

    @property
    def id_pago(self):
        return self.__id_pago

    @property
    def id_factura(self):
        return self.__id_factura

    @property
    def documento_paciente(self):
        return self.__documento_paciente

    @property
    def fecha(self):
        return self.__fecha

    @property
    def valor_pagado(self):
        return self.__valor_pagado

    @property
    def metodo_pago(self):
        return self.__metodo_pago

    def to_dict(self):
        return {
            "id_pago": self.__id_pago,
            "id_factura": self.__id_factura,
            "documento_paciente": self.__documento_paciente,
            "fecha": self.__fecha,
            "valor_pagado": self.__valor_pagado,
            "metodo_pago": self.__metodo_pago,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id_factura=data.get("id_factura", ""),
            documento_paciente=data.get("documento_paciente", ""),
            fecha=data.get("fecha"),
            valor_pagado=data.get("valor_pagado", 0),
            metodo_pago=data.get("metodo_pago", ""),
            id_pago=data.get("id_pago"),
        )
