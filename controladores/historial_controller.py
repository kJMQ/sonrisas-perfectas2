from __future__ import annotations

from controladores.paciente_controller import PacienteController
from modelos.historial_medico import HistorialMedico
from utils.json_manager import JsonManager
from utils.validaciones import Validaciones


class HistorialController:
    def __init__(self, ruta_db="historiales.json", paciente_controller=None):
        self.ruta_db = ruta_db
        self.paciente_controller = paciente_controller or PacienteController()

    def listar_todos(self):
        registros = JsonManager.leer(self.ruta_db, [])
        normalizados = [HistorialMedico.from_dict(item).to_dict() for item in registros]
        if registros != normalizados:
            JsonManager.guardar(self.ruta_db, normalizados)
        return normalizados

    def registrar_entrada(self, registro_obj):
        registro = (
            registro_obj
            if isinstance(registro_obj, HistorialMedico)
            else HistorialMedico.from_dict(registro_obj)
        )
        valido, mensaje = Validaciones.validar_campos_obligatorios(
            {
                "documento del paciente": registro.documento_paciente,
                "odontólogo": registro.odontologo,
                "diagnóstico": registro.diagnostico,
                "tratamiento": registro.tratamiento,
            }
        )
        if not valido:
            return False, mensaje

        paciente = self.paciente_controller.buscar_por_documento(registro.documento_paciente)
        if not paciente:
            return False, "El paciente no está registrado."

        historiales = self.listar_todos()
        historiales.append(registro.to_dict())
        JsonManager.guardar(self.ruta_db, historiales)

        historial_paciente = list(paciente.get("historial", []))
        if registro.id_registro not in historial_paciente:
            historial_paciente.append(registro.id_registro)
            self.paciente_controller.actualizar_paciente(
                registro.documento_paciente,
                {"historial": historial_paciente},
            )

        return True, "Registro clínico guardado correctamente."

    def consultar_por_paciente(self, documento):
        documento = str(documento).strip()
        return [
            registro
            for registro in self.listar_todos()
            if registro.get("documento_paciente") == documento
        ]
