from __future__ import annotations

from datetime import datetime

from controladores.paciente_controller import PacienteController
from modelos.cita import Cita
from utils.helpers import combinar_fecha_hora
from utils.json_manager import JsonManager
from utils.validaciones import Validaciones


class CitaController:
    def __init__(self, ruta_db="citas.json", paciente_controller=None):
        self.ruta_db = ruta_db
        self.paciente_controller = paciente_controller or PacienteController()

    def _normalizar_registros(self):
        registros = JsonManager.leer(self.ruta_db, [])
        normalizados = [Cita.from_dict(item).to_dict() for item in registros]
        if registros != normalizados:
            JsonManager.guardar(self.ruta_db, normalizados)
        return normalizados

    def listar_todas(self):
        return self._normalizar_registros()

    def validar_disponibilidad(self, fecha, hora, odontologo, id_actual=None):
        for cita in self.listar_todas():
            if cita.get("id_cita") == id_actual:
                continue
            if cita.get("estado") == "Cancelada":
                continue
            if (
                cita.get("fecha") == fecha
                and cita.get("hora") == hora
                and cita.get("odontologo") == odontologo
            ):
                return False, "El odontólogo ya tiene una cita asignada en ese horario."
        return True, ""

    def agendar_cita(self, cita_obj, lista_pacientes_registrados=None):
        cita = cita_obj if isinstance(cita_obj, Cita) else Cita.from_dict(cita_obj)
        valido, mensaje = Validaciones.validar_campos_obligatorios(
            {
                "documento del paciente": cita.documento_paciente,
                "fecha": cita.fecha,
                "hora": cita.hora,
                "motivo": cita.motivo,
                "odontólogo": cita.odontologo,
            }
        )
        if not valido:
            return False, mensaje

        valido, mensaje = Validaciones.validar_fecha_hora(cita.fecha, cita.hora)
        if not valido:
            return False, mensaje

        pacientes = lista_pacientes_registrados or self.paciente_controller.listar_pacientes()
        paciente = next(
            (item for item in pacientes if item.get("documento") == cita.documento_paciente),
            None,
        )
        if not paciente:
            return False, "El paciente no está registrado en el sistema."

        citas = self.listar_todas()
        for registro in citas:
            if (
                registro.get("documento_paciente") == cita.documento_paciente
                and registro.get("fecha") == cita.fecha
                and registro.get("hora") == cita.hora
                and registro.get("estado") != "Cancelada"
            ):
                return False, "El paciente ya tiene una cita en esa fecha y hora."

        valido, mensaje = self.validar_disponibilidad(cita.fecha, cita.hora, cita.odontologo)
        if not valido:
            return False, mensaje

        datos_cita = cita.to_dict()
        if not datos_cita.get("nombre_paciente"):
            datos_cita["nombre_paciente"] = paciente.get("nombre", "")

        citas.append(datos_cita)
        JsonManager.guardar(self.ruta_db, citas)
        return True, "Cita agendada exitosamente."

    def buscar_por_paciente(self, documento):
        documento = str(documento).strip()
        return [
            cita for cita in self.listar_todas() if cita.get("documento_paciente") == documento
        ]

    def modificar_cita(self, id_cita, datos_actualizados):
        citas = self.listar_todas()
        for indice, cita in enumerate(citas):
            if cita.get("id_cita") != id_cita:
                continue

            cita_actualizada = dict(cita)
            cita_actualizada.update(datos_actualizados)
            cita_obj = Cita.from_dict(cita_actualizada)

            paciente = self.paciente_controller.buscar_por_documento(cita_obj.documento_paciente)
            if not paciente:
                return False, "No existe el paciente asociado a la cita."

            valido, mensaje = Validaciones.validar_fecha_hora(cita_obj.fecha, cita_obj.hora)
            if not valido:
                return False, mensaje

            valido, mensaje = self.validar_disponibilidad(
                cita_obj.fecha,
                cita_obj.hora,
                cita_obj.odontologo,
                id_actual=id_cita,
            )
            if not valido:
                return False, mensaje

            datos = cita_obj.to_dict()
            if not datos.get("nombre_paciente"):
                datos["nombre_paciente"] = paciente.get("nombre", "")

            citas[indice] = datos
            JsonManager.guardar(self.ruta_db, citas)
            return True, "Cita modificada correctamente."

        return False, "No se encontró la cita solicitada."

    def cancelar_cita(self, id_cita):
        return self.modificar_cita(id_cita, {"estado": "Cancelada"})

    def citas_por_rango(self, fecha_inicio, fecha_fin):
        fecha_desde = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fecha_hasta = datetime.strptime(fecha_fin, "%Y-%m-%d")
        resultado = []
        for cita in self.listar_todas():
            fecha_cita = datetime.strptime(cita.get("fecha"), "%Y-%m-%d")
            if fecha_desde <= fecha_cita <= fecha_hasta:
                resultado.append(cita)
        return resultado
