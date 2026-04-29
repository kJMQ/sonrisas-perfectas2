from __future__ import annotations

from controladores.usuario_controller import UsuarioController
from utils.validaciones import Validaciones


class AuthController:
    def __init__(self, usuario_controller=None):
        self.usuario_controller = usuario_controller or UsuarioController()

    def iniciar_sesion(self, username, password, codigo_mfa=""):
        valido, mensaje = Validaciones.validar_login(username, password)
        if not valido:
            return False, mensaje, None

        usuario = self.usuario_controller.buscar_usuario(username)
        if not usuario:
            self.usuario_controller.registrar_bitacora(
                username,
                "login",
                "Intento de acceso con usuario inexistente.",
                "ERROR",
            )
            return False, "Usuario no encontrado.", None

        if not usuario.get("activo", True):
            self.usuario_controller.registrar_bitacora(
                usuario,
                "login",
                "Intento de acceso con usuario inactivo.",
                "ERROR",
            )
            return False, "El usuario está inactivo.", None

        if usuario.get("password") != str(password).strip():
            self.usuario_controller.registrar_bitacora(
                usuario,
                "login",
                "Contraseña incorrecta.",
                "ERROR",
            )
            return False, "Contraseña incorrecta.", None

        if usuario.get("mfa_habilitado") and str(codigo_mfa).strip() != "123456":
            self.usuario_controller.registrar_bitacora(
                usuario,
                "login",
                "Código MFA incorrecto.",
                "ERROR",
            )
            return False, "Código MFA inválido. Usa 123456 para la simulación académica.", None

        self.usuario_controller.registrar_bitacora(
            usuario,
            "login",
            "Inicio de sesión exitoso.",
            "OK",
        )
        return True, "Inicio de sesión correcto.", usuario

    def cerrar_sesion(self, usuario):
        self.usuario_controller.registrar_bitacora(
            usuario,
            "logout",
            "Cierre de sesión.",
            "OK",
        )

    def obtener_permisos(self, usuario):
        rol = self.usuario_controller.obtener_rol(usuario.get("rol", ""))
        return rol.get("permisos", []) if rol else []

    def tiene_permiso(self, usuario, permiso):
        return permiso in self.obtener_permisos(usuario)
