from __future__ import annotations

from utils.helpers import dividir_fecha_hora, generar_id, limpiar_texto


class Cita:
    """Representa una cita dental del sistema."""

    def __init__(
        self,
        documento_paciente,
        fecha,
        motivo="",
        odontologo="Dr. Pérez",
        estado="Activa",
        id_cita=None,
        nombre_paciente="",
        hora=None,
    ):
        fecha_normalizada, hora_normalizada = dividir_fecha_hora(fecha, hora or "")
        self.__id_cita = limpiar_texto(id_cita) or generar_id("CITA")
        self.__documento_paciente = limpiar_texto(documento_paciente)
        self.__nombre_paciente = limpiar_texto(nombre_paciente)
        self.__fecha = fecha_normalizada
        self.__hora = hora_normalizada
        self.__motivo = limpiar_texto(motivo)
        self.__odontologo = limpiar_texto(odontologo) or "Dr. Pérez"
        self.__estado = limpiar_texto(estado) or "Activa"

    @property
    def id_cita(self):
        return self.__id_cita

    @property
    def documento_paciente(self):
        return self.__documento_paciente

    @property
    def doc_paciente(self):
        return self.__documento_paciente

    @property
    def nombre_paciente(self):
        return self.__nombre_paciente

    @property
    def fecha(self):
        return self.__fecha

    @property
    def hora(self):
        return self.__hora

    @property
    def motivo(self):
        return self.__motivo

    @property
    def odontologo(self):
        return self.__odontologo

    @property
    def estado(self):
        return self.__estado

    @estado.setter
    def estado(self, valor):
        self.__estado = limpiar_texto(valor)

    def to_dict(self):
        return {
            "id_cita": self.__id_cita,
            "documento_paciente": self.__documento_paciente,
            "nombre_paciente": self.__nombre_paciente,
            "fecha": self.__fecha,
            "hora": self.__hora,
            "motivo": self.__motivo,
            "odontologo": self.__odontologo,
            "estado": self.__estado,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            documento_paciente=data.get("documento_paciente") or data.get("doc_paciente", ""),
            nombre_paciente=data.get("nombre_paciente", ""),
            fecha=data.get("fecha", ""),
            hora=data.get("hora"),
            motivo=data.get("motivo", ""),
            odontologo=data.get("odontologo", "Dr. Pérez"),
            estado=data.get("estado", "Activa"),
            id_cita=data.get("id_cita"),
        )
