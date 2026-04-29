from __future__ import annotations

from utils.helpers import fecha_hora_actual, generar_id, limpiar_texto


class Notificacion:
    def __init__(
        self,
        documento_paciente,
        tipo,
        mensaje,
        estado="Pendiente",
        fecha_creacion=None,
        id_notificacion=None,
        referencia="",
    ):
        self.__id_notificacion = limpiar_texto(id_notificacion) or generar_id("NOT")
        self.__documento_paciente = limpiar_texto(documento_paciente)
        self.__tipo = limpiar_texto(tipo)
        self.__mensaje = limpiar_texto(mensaje)
        self.__estado = limpiar_texto(estado) or "Pendiente"
        self.__fecha_creacion = limpiar_texto(fecha_creacion) or fecha_hora_actual()
        self.__referencia = limpiar_texto(referencia)

    @property
    def id_notificacion(self):
        return self.__id_notificacion

    @property
    def documento_paciente(self):
        return self.__documento_paciente

    @property
    def tipo(self):
        return self.__tipo

    @property
    def mensaje(self):
        return self.__mensaje

    @property
    def estado(self):
        return self.__estado

    @estado.setter
    def estado(self, valor):
        self.__estado = limpiar_texto(valor)

    @property
    def fecha_creacion(self):
        return self.__fecha_creacion

    @property
    def referencia(self):
        return self.__referencia

    def to_dict(self):
        return {
            "id_notificacion": self.__id_notificacion,
            "documento_paciente": self.__documento_paciente,
            "tipo": self.__tipo,
            "mensaje": self.__mensaje,
            "estado": self.__estado,
            "fecha_creacion": self.__fecha_creacion,
            "referencia": self.__referencia,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            documento_paciente=data.get("documento_paciente", ""),
            tipo=data.get("tipo", ""),
            mensaje=data.get("mensaje", ""),
            estado=data.get("estado", "Pendiente"),
            fecha_creacion=data.get("fecha_creacion"),
            id_notificacion=data.get("id_notificacion"),
            referencia=data.get("referencia", ""),
        )
