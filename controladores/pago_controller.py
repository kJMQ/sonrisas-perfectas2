from __future__ import annotations

from controladores.factura_controller import FacturaController
from modelos.pago import Pago
from utils.json_manager import JsonManager
from utils.validaciones import Validaciones


class PagoController:
    def __init__(self, ruta_db="pagos.json", factura_controller=None):
        self.ruta_db = ruta_db
        self.factura_controller = factura_controller or FacturaController()

    def listar_pagos(self):
        registros = JsonManager.leer(self.ruta_db, [])
        normalizados = [Pago.from_dict(item).to_dict() for item in registros]
        if registros != normalizados:
            JsonManager.guardar(self.ruta_db, normalizados)
        return normalizados

    def obtener_pagos_por_factura(self, id_factura):
        return [pago for pago in self.listar_pagos() if pago.get("id_factura") == id_factura]

    def calcular_total_pagado(self, id_factura):
        return sum(pago.get("valor_pagado", 0) for pago in self.obtener_pagos_por_factura(id_factura))

    def calcular_saldo_pendiente(self, id_factura):
        factura = self.factura_controller.obtener_factura(id_factura)
        if not factura:
            return None
        return max(float(factura.get("valor_total", 0)) - self.calcular_total_pagado(id_factura), 0.0)

    def registrar_pago(self, pago_obj):
        pago = pago_obj if isinstance(pago_obj, Pago) else Pago.from_dict(pago_obj)
        valido, mensaje = Validaciones.validar_campos_obligatorios(
            {
                "id de factura": pago.id_factura,
                "valor pagado": pago.valor_pagado,
                "método de pago": pago.metodo_pago,
            }
        )
        if not valido:
            return False, mensaje

        valido, mensaje = Validaciones.validar_monto_positivo(pago.valor_pagado, "valor pagado")
        if not valido:
            return False, mensaje

        factura = self.factura_controller.obtener_factura(pago.id_factura)
        if not factura:
            return False, "La factura indicada no existe."

        saldo = self.calcular_saldo_pendiente(pago.id_factura)
        if saldo is None:
            return False, "No fue posible calcular el saldo de la factura."
        if pago.valor_pagado > saldo:
            return False, "El valor pagado supera el saldo pendiente."

        datos = pago.to_dict()
        if not datos.get("documento_paciente"):
            datos["documento_paciente"] = factura.get("documento_paciente", "")

        pagos = self.listar_pagos()
        pagos.append(datos)
        JsonManager.guardar(self.ruta_db, pagos)

        total_pagado = self.calcular_total_pagado(pago.id_factura)
        self.factura_controller.actualizar_estado_factura(pago.id_factura, total_pagado)
        return True, "Pago registrado correctamente."

    def historial_financiero_por_paciente(self, documento):
        facturas = self.factura_controller.buscar_por_paciente(documento)
        pagos = [pago for pago in self.listar_pagos() if pago.get("documento_paciente") == str(documento).strip()]
        saldo_total = sum(self.calcular_saldo_pendiente(factura.get("id_factura")) or 0 for factura in facturas)
        return {
            "facturas": facturas,
            "pagos": pagos,
            "saldo_total": saldo_total,
        }
