from __future__ import annotations

from controladores.paciente_controller import PacienteController
from modelos.factura import Factura
from utils.json_manager import JsonManager
from utils.validaciones import Validaciones


class FacturaController:
    def __init__(self, ruta_db="facturas.json", paciente_controller=None):
        self.ruta_db = ruta_db
        self.paciente_controller = paciente_controller or PacienteController()

    def listar_facturas(self):
        registros = JsonManager.leer(self.ruta_db, [])
        normalizados = [Factura.from_dict(item).to_dict() for item in registros]
        if registros != normalizados:
            JsonManager.guardar(self.ruta_db, normalizados)
        return normalizados

    def generar_factura(self, factura_obj):
        factura = factura_obj if isinstance(factura_obj, Factura) else Factura.from_dict(factura_obj)

        valido, mensaje = Validaciones.validar_campos_obligatorios(
            {
                "documento del paciente": factura.documento_paciente,
                "concepto": factura.concepto,
                "valor total": factura.valor_total,
            }
        )
        if not valido:
            return False, mensaje

        valido, mensaje = Validaciones.validar_monto_positivo(factura.valor_total, "valor total")
        if not valido:
            return False, mensaje

        paciente = self.paciente_controller.buscar_por_documento(factura.documento_paciente)
        if not paciente:
            return False, "El paciente no está registrado."

        datos = factura.to_dict()
        if not datos.get("nombre_paciente"):
            datos["nombre_paciente"] = paciente.get("nombre", "")

        facturas = self.listar_facturas()
        facturas.append(datos)
        JsonManager.guardar(self.ruta_db, facturas)
        return True, "Factura generada correctamente."

    def buscar_por_paciente(self, documento):
        documento = str(documento).strip()
        return [
            factura
            for factura in self.listar_facturas()
            if factura.get("documento_paciente") == documento
        ]

    def obtener_factura(self, id_factura):
        for factura in self.listar_facturas():
            if factura.get("id_factura") == id_factura:
                return factura
        return None

    def actualizar_estado_factura(self, id_factura, monto_pagado):
        facturas = self.listar_facturas()
        for indice, factura in enumerate(facturas):
            if factura.get("id_factura") != id_factura:
                continue

            total = float(factura.get("valor_total", 0))
            if monto_pagado >= total:
                factura["estado_pago"] = "Pagada"
            elif monto_pagado > 0:
                factura["estado_pago"] = "Abonada"
            else:
                factura["estado_pago"] = "Pendiente"

            facturas[indice] = factura
            JsonManager.guardar(self.ruta_db, facturas)
            return True
        return False
