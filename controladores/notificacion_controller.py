from __future__ import annotations

from controladores.paciente_controller import PacienteController
from modelos.notificacion import Notificacion
from utils.json_manager import JsonManager
from utils.validaciones import Validaciones


class NotificacionController:
    def __init__(self, ruta_db="notificaciones.json", paciente_controller=None):
        self.ruta_db = ruta_db
        self.paciente_controller = paciente_controller or PacienteController()

    def listar_notificaciones(self):
        registros = JsonManager.leer(self.ruta_db, [])
        normalizados = [Notificacion.from_dict(item).to_dict() for item in registros]
        if registros != normalizados:
            JsonManager.guardar(self.ruta_db, normalizados)
        return normalizados

    def registrar_notificacion(self, notificacion_obj):
        notificacion = (
            notificacion_obj
            if isinstance(notificacion_obj, Notificacion)
            else Notificacion.from_dict(notificacion_obj)
        )
        valido, mensaje = Validaciones.validar_campos_obligatorios(
            {
                "documento del paciente": notificacion.documento_paciente,
                "tipo": notificacion.tipo,
                "mensaje": notificacion.mensaje,
            }
        )
        if not valido:
            return False, mensaje

        paciente = self.paciente_controller.buscar_por_documento(notificacion.documento_paciente)
        if not paciente:
            return False, "El paciente no existe."

        registros = self.listar_notificaciones()
        registros.append(notificacion.to_dict())
        JsonManager.guardar(self.ruta_db, registros)
        return True, "Notificación registrada correctamente."

    def buscar_por_paciente(self, documento):
        documento = str(documento).strip()
        return [
            notificacion
            for notificacion in self.listar_notificaciones()
            if notificacion.get("documento_paciente") == documento
        ]

    def cambiar_estado(self, id_notificacion, estado):
        registros = self.listar_notificaciones()
        for indice, item in enumerate(registros):
            if item.get("id_notificacion") == id_notificacion:
                item["estado"] = estado
                registros[indice] = item
                JsonManager.guardar(self.ruta_db, registros)
                return True, "Estado actualizado."
        return False, "No se encontró la notificación."

    def crear_confirmacion_cita(self, cita):
        mensaje = (
            f"Su cita quedó agendada para el {cita.get('fecha')} a las {cita.get('hora')} "
            f"con {cita.get('odontologo')}."
        )
        return self.registrar_notificacion(
            Notificacion(
                documento_paciente=cita.get("documento_paciente"),
                tipo="Confirmación de cita",
                mensaje=mensaje,
                referencia=cita.get("id_cita", ""),
                estado="Registrada",
            )
        )

    def crear_recordatorio_cita(self, cita):
        mensaje = (
            f"Recordatorio: tiene una cita el {cita.get('fecha')} a las {cita.get('hora')} "
            f"por motivo '{cita.get('motivo')}'."
        )
        return self.registrar_notificacion(
            Notificacion(
                documento_paciente=cita.get("documento_paciente"),
                tipo="Recordatorio",
                mensaje=mensaje,
                referencia=cita.get("id_cita", ""),
                estado="Pendiente",
            )
        )
