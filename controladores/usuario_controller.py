from __future__ import annotations

from modelos.rol import Rol
from modelos.usuario import Usuario
from utils.helpers import fecha_hora_actual
from utils.json_manager import JsonManager
from utils.validaciones import Validaciones


ROLES_PREDETERMINADOS = [
    Rol(
        "administrador",
        ["pacientes", "citas", "historial", "facturacion", "reportes", "notificaciones", "seguridad"],
        "Acceso completo a la operación académica.",
    ),
    Rol(
        "recepcionista",
        ["pacientes", "citas", "facturacion", "notificaciones"],
        "Gestiona agenda, pacientes y cobros básicos.",
    ),
    Rol(
        "odontologo",
        ["pacientes", "citas", "historial", "reportes"],
        "Consulta agenda y actualiza historial clínico.",
    ),
    Rol(
        "gerente",
        ["reportes", "seguridad"],
        "Consulta reportes y administra respaldos.",
    ),
]

USUARIOS_PREDETERMINADOS = [
    Usuario("admin", "admin123", "Administrador General", "administrador"),
    Usuario("recepcion", "recepcion123", "Recepcionista", "recepcionista"),
    Usuario("doctor", "doctor123", "Dr. Sofía Herrera", "odontologo", mfa_habilitado=True),
    Usuario("gerencia", "gerencia123", "Gerencia", "gerente", mfa_habilitado=True),
]


class UsuarioController:
    def __init__(
        self,
        ruta_usuarios="usuarios.json",
        ruta_roles="roles.json",
        ruta_bitacora="bitacora.json",
    ):
        self.ruta_usuarios = ruta_usuarios
        self.ruta_roles = ruta_roles
        self.ruta_bitacora = ruta_bitacora
        self._asegurar_datos_base()

    def _asegurar_datos_base(self):
        roles = JsonManager.leer(self.ruta_roles, [])
        usuarios = JsonManager.leer(self.ruta_usuarios, [])
        JsonManager.leer(self.ruta_bitacora, [])

        if not roles:
            JsonManager.guardar(self.ruta_roles, [rol.to_dict() for rol in ROLES_PREDETERMINADOS])
        else:
            normalizados = [Rol.from_dict(item).to_dict() for item in roles]
            if roles != normalizados:
                JsonManager.guardar(self.ruta_roles, normalizados)

        if not usuarios:
            JsonManager.guardar(
                self.ruta_usuarios,
                [usuario.to_dict() for usuario in USUARIOS_PREDETERMINADOS],
            )
        else:
            normalizados = [Usuario.from_dict(item).to_dict() for item in usuarios]
            if usuarios != normalizados:
                JsonManager.guardar(self.ruta_usuarios, normalizados)

    def listar_roles(self):
        return JsonManager.leer(self.ruta_roles, [])

    def listar_usuarios(self):
        return JsonManager.leer(self.ruta_usuarios, [])

    def buscar_usuario(self, username):
        username = str(username).strip().lower()
        for usuario in self.listar_usuarios():
            if usuario.get("username", "").lower() == username:
                return usuario
        return None

    def obtener_rol(self, nombre_rol):
        nombre_rol = str(nombre_rol).strip().lower()
        for rol in self.listar_roles():
            if rol.get("nombre", "").lower() == nombre_rol:
                return rol
        return None

    def registrar_usuario(self, usuario_obj):
        usuario = usuario_obj if isinstance(usuario_obj, Usuario) else Usuario.from_dict(usuario_obj)
        valido, mensaje = Validaciones.validar_campos_obligatorios(
            {
                "usuario": usuario.username,
                "contraseña": usuario.password,
                "nombre": usuario.nombre,
                "rol": usuario.rol,
            }
        )
        if not valido:
            return False, mensaje

        usuarios = self.listar_usuarios()
        valido, mensaje = Validaciones.validar_username_unico(usuario.username, usuarios)
        if not valido:
            return False, mensaje

        if not self.obtener_rol(usuario.rol):
            return False, "El rol seleccionado no existe."

        usuarios.append(usuario.to_dict())
        JsonManager.guardar(self.ruta_usuarios, usuarios)
        return True, "Usuario registrado correctamente."

    def registrar_bitacora(self, usuario, accion, detalle, resultado="OK"):
        bitacora = JsonManager.leer(self.ruta_bitacora, [])
        if isinstance(usuario, dict):
            username = usuario.get("username", "sistema")
            rol = usuario.get("rol", "sistema")
        else:
            username = str(usuario or "sistema")
            rol = "sistema"

        bitacora.append(
            {
                "fecha": fecha_hora_actual(),
                "usuario": username,
                "rol": rol,
                "accion": accion,
                "detalle": detalle,
                "resultado": resultado,
            }
        )
        JsonManager.guardar(self.ruta_bitacora, bitacora)

    def listar_bitacora(self):
        return JsonManager.leer(self.ruta_bitacora, [])
