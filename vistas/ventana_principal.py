from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from controladores.auth_controller import AuthController
from controladores.cita_controller import CitaController
from controladores.factura_controller import FacturaController
from controladores.historial_controller import HistorialController
from controladores.notificacion_controller import NotificacionController
from controladores.paciente_controller import PacienteController
from controladores.pago_controller import PagoController
from controladores.reporte_controller import ReporteController
from controladores.usuario_controller import UsuarioController
from utils.backup_manager import BackupManager
from vistas.citas_view import CitasView
from vistas.facturacion_view import FacturacionView
from vistas.historial_view import HistorialView
from vistas.notificaciones_view import NotificacionesView
from vistas.pacientes_view import PacientesView
from vistas.reportes_view import ReportesView
from vistas.seguridad_view import SeguridadView


class VentanaPrincipalClinica(QMainWindow):
    cerrar_sesion_solicitada = Signal()

    def __init__(self, usuario_actual, parent=None):
        super().__init__(parent)
        self.usuario_actual = usuario_actual
        self._sesion_cerrada = False
        self.setWindowTitle("Sistema de Gestión Clínica Dental Sonrisa Perfecta")
        self.resize(1200, 760)

        self.usuario_controller = UsuarioController()
        self.auth_controller = AuthController(self.usuario_controller)
        self.paciente_controller = PacienteController()
        self.cita_controller = CitaController(paciente_controller=self.paciente_controller)
        self.historial_controller = HistorialController(paciente_controller=self.paciente_controller)
        self.factura_controller = FacturaController(paciente_controller=self.paciente_controller)
        self.pago_controller = PagoController(factura_controller=self.factura_controller)
        self.notificacion_controller = NotificacionController(
            paciente_controller=self.paciente_controller
        )
        self.reporte_controller = ReporteController(
            paciente_controller=self.paciente_controller,
            cita_controller=self.cita_controller,
            historial_controller=self.historial_controller,
            factura_controller=self.factura_controller,
            pago_controller=self.pago_controller,
        )

        self._construir_ui()

    def _construir_ui(self):
        contenedor = QWidget()
        layout = QVBoxLayout(contenedor)

        encabezado = QHBoxLayout()
        permisos = ", ".join(self.auth_controller.obtener_permisos(self.usuario_actual))
        etiqueta = QLabel(
            f"Usuario: {self.usuario_actual.get('nombre')} | "
            f"Rol: {self.usuario_actual.get('rol')} | "
            f"Permisos: {permisos}"
        )
        encabezado.addWidget(etiqueta)

        self.boton_backup = QPushButton("Backup rápido")
        self.boton_backup.clicked.connect(self.crear_backup_rapido)
        self.boton_backup.setVisible(
            self.auth_controller.tiene_permiso(self.usuario_actual, "seguridad")
        )
        encabezado.addWidget(self.boton_backup)

        boton_logout = QPushButton("Cerrar sesión")
        boton_logout.clicked.connect(self.cerrar_sesion)
        encabezado.addWidget(boton_logout)
        layout.addLayout(encabezado)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self.setCentralWidget(contenedor)
        self._construir_tabs()
        self.tabs.currentChanged.connect(lambda _: self.refrescar_vistas())

    def _construir_tabs(self):
        permisos = set(self.auth_controller.obtener_permisos(self.usuario_actual))
        self.vistas = []

        if "pacientes" in permisos:
            vista = PacientesView(self.paciente_controller, on_change=self.refrescar_vistas)
            self.tabs.addTab(vista, "Pacientes")
            self.vistas.append(vista)

        if "citas" in permisos:
            vista = CitasView(
                self.cita_controller,
                self.paciente_controller,
                self.notificacion_controller,
                self.usuario_controller,
                on_change=self.refrescar_vistas,
            )
            self.tabs.addTab(vista, "Citas")
            self.vistas.append(vista)

        if "historial" in permisos:
            vista = HistorialView(
                self.historial_controller,
                self.paciente_controller,
                self.usuario_controller,
                on_change=self.refrescar_vistas,
            )
            self.tabs.addTab(vista, "Historial médico")
            self.vistas.append(vista)

        if "facturacion" in permisos:
            vista = FacturacionView(
                self.factura_controller,
                self.pago_controller,
                self.paciente_controller,
                on_change=self.refrescar_vistas,
            )
            self.tabs.addTab(vista, "Facturación y pagos")
            self.vistas.append(vista)

        if "reportes" in permisos:
            vista = ReportesView(self.reporte_controller)
            self.tabs.addTab(vista, "Reportes")
            self.vistas.append(vista)

        if "notificaciones" in permisos:
            vista = NotificacionesView(self.notificacion_controller)
            self.tabs.addTab(vista, "Notificaciones")
            self.vistas.append(vista)

        if "seguridad" in permisos:
            vista = SeguridadView(
                self.usuario_controller,
                self.usuario_actual,
                on_change=self.refrescar_vistas,
            )
            self.tabs.addTab(vista, "Seguridad")
            self.vistas.append(vista)

    def refrescar_vistas(self):
        for vista in self.vistas:
            refrescar = getattr(vista, "refrescar_datos", None)
            if callable(refrescar):
                refrescar()

    def crear_backup_rapido(self):
        respaldo = BackupManager.crear_respaldo()
        self.usuario_controller.registrar_bitacora(
            self.usuario_actual,
            "backup_rapido",
            f"Backup rápido en {respaldo['destino']}.",
            "OK",
        )
        QMessageBox.information(
            self,
            "Backup",
            f"Se copiaron {respaldo['archivos']} archivos en:\n{respaldo['destino']}",
        )
        self.refrescar_vistas()

    def cerrar_sesion(self):
        self._sesion_cerrada = True
        self.auth_controller.cerrar_sesion(self.usuario_actual)
        self.close()
        self.cerrar_sesion_solicitada.emit()

    def closeEvent(self, event):
        if not self._sesion_cerrada:
            self.auth_controller.cerrar_sesion(self.usuario_actual)
        super().closeEvent(event)
