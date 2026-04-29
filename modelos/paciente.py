from __future__ import annotations

from utils.helpers import limpiar_texto


class Paciente:
    """Entidad Paciente con encapsulamiento sencillo."""

    def __init__(
        self,
        documento,
        nombre,
        telefono,
        correo="",
        direccion="",
        historial=None,
    ):
        self.__documento = limpiar_texto(documento)
        self.__nombre = limpiar_texto(nombre)
        self.__telefono = limpiar_texto(telefono)
        self.__correo = limpiar_texto(correo)
        self.__direccion = limpiar_texto(direccion)
        self.__historial = list(historial or [])

    @property
    def documento(self):
        return self.__documento

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        self.__nombre = limpiar_texto(valor)

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        self.__telefono = limpiar_texto(valor)

    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, valor):
        self.__correo = limpiar_texto(valor)

    @property
    def direccion(self):
        return self.__direccion

    @direccion.setter
    def direccion(self, valor):
        self.__direccion = limpiar_texto(valor)

    @property
    def historial(self):
        return list(self.__historial)

    def agregar_historial(self, id_historial):
        if id_historial and id_historial not in self.__historial:
            self.__historial.append(id_historial)

    def to_dict(self):
        return {
            "documento": self.__documento,
            "nombre": self.__nombre,
            "telefono": self.__telefono,
            "correo": self.__correo,
            "direccion": self.__direccion,
            "historial": list(self.__historial),
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            documento=data.get("documento", ""),
            nombre=data.get("nombre", ""),
            telefono=data.get("telefono", ""),
            correo=data.get("correo", ""),
            direccion=data.get("direccion", ""),
            historial=data.get("historial", []),
        )
