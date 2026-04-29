from __future__ import annotations

from utils.helpers import generar_id, limpiar_texto


class Usuario:
    def __init__(
        self,
        username,
        password,
        nombre,
        rol,
        activo=True,
        mfa_habilitado=False,
        id_usuario=None,
    ):
        self.__id_usuario = limpiar_texto(id_usuario) or generar_id("USR")
        self.__username = limpiar_texto(username)
        self.__password = limpiar_texto(password)
        self.__nombre = limpiar_texto(nombre)
        self.__rol = limpiar_texto(rol)
        self.__activo = bool(activo)
        self.__mfa_habilitado = bool(mfa_habilitado)

    @property
    def id_usuario(self):
        return self.__id_usuario

    @property
    def username(self):
        return self.__username

    @property
    def password(self):
        return self.__password

    @property
    def nombre(self):
        return self.__nombre

    @property
    def rol(self):
        return self.__rol

    @property
    def activo(self):
        return self.__activo

    @property
    def mfa_habilitado(self):
        return self.__mfa_habilitado

    def to_dict(self):
        return {
            "id_usuario": self.__id_usuario,
            "username": self.__username,
            "password": self.__password,
            "nombre": self.__nombre,
            "rol": self.__rol,
            "activo": self.__activo,
            "mfa_habilitado": self.__mfa_habilitado,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            username=data.get("username", ""),
            password=data.get("password", ""),
            nombre=data.get("nombre", ""),
            rol=data.get("rol", ""),
            activo=data.get("activo", True),
            mfa_habilitado=data.get("mfa_habilitado", False),
            id_usuario=data.get("id_usuario"),
        )
