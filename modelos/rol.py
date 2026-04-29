from __future__ import annotations

from utils.helpers import limpiar_texto


class Rol:
    def __init__(self, nombre, permisos, descripcion=""):
        self.__nombre = limpiar_texto(nombre)
        self.__permisos = list(permisos or [])
        self.__descripcion = limpiar_texto(descripcion)

    @property
    def nombre(self):
        return self.__nombre

    @property
    def permisos(self):
        return list(self.__permisos)

    @property
    def descripcion(self):
        return self.__descripcion

    def to_dict(self):
        return {
            "nombre": self.__nombre,
            "permisos": list(self.__permisos),
            "descripcion": self.__descripcion,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            nombre=data.get("nombre", ""),
            permisos=data.get("permisos", []),
            descripcion=data.get("descripcion", ""),
        )
