from __future__ import annotations

from utils.helpers import fecha_hora_actual, generar_id, limpiar_texto


class HistorialMedico:
    def __init__(
        self,
        documento_paciente,
        odontologo,
        diagnostico,
        tratamiento,
        observaciones="",
        fecha=None,
        id_registro=None,
    ):
        self.__id_registro = limpiar_texto(id_registro) or generar_id("HIST")
        self.__documento_paciente = limpiar_texto(documento_paciente)
        self.__fecha = limpiar_texto(fecha) or fecha_hora_actual()
        self.__odontologo = limpiar_texto(odontologo)
        self.__diagnostico = limpiar_texto(diagnostico)
        self.__tratamiento = limpiar_texto(tratamiento)
        self.__observaciones = limpiar_texto(observaciones)

    @property
    def id_registro(self):
        return self.__id_registro

    @property
    def documento_paciente(self):
        return self.__documento_paciente

    @property
    def fecha(self):
        return self.__fecha

    @property
    def odontologo(self):
        return self.__odontologo

    @property
    def diagnostico(self):
        return self.__diagnostico

    @property
    def tratamiento(self):
        return self.__tratamiento

    @property
    def observaciones(self):
        return self.__observaciones

    def to_dict(self):
        return {
            "id_registro": self.__id_registro,
            "documento_paciente": self.__documento_paciente,
            "fecha": self.__fecha,
            "odontologo": self.__odontologo,
            "diagnostico": self.__diagnostico,
            "tratamiento": self.__tratamiento,
            "observaciones": self.__observaciones,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            documento_paciente=data.get("documento_paciente", ""),
            fecha=data.get("fecha"),
            odontologo=data.get("odontologo", ""),
            diagnostico=data.get("diagnostico", ""),
            tratamiento=data.get("tratamiento", ""),
            observaciones=data.get("observaciones", ""),
            id_registro=data.get("id_registro"),
        )
