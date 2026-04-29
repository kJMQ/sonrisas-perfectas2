from __future__ import annotations

from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFormLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from modelos.notificacion import Notificacion


class NotificacionesView(QWidget):
    def __init__(self, notificacion_controller, parent=None):
        super().__init__(parent)
        self.notificacion_controller = notificacion_controller
        self._construir_ui()
        self.refrescar_datos()

    def _construir_ui(self):
        layout = QVBoxLayout(self)

        formulario = QFormLayout()
        self.input_documento = QLineEdit()
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Recordatorio", "Confirmación de cita", "Informativa"])
        self.input_mensaje = QTextEdit()
        formulario.addRow("Documento paciente:", self.input_documento)
        formulario.addRow("Tipo:", self.combo_tipo)
        formulario.addRow("Mensaje:", self.input_mensaje)
        layout.addLayout(formulario)

        boton_registrar = QPushButton("Registrar notificación")
        boton_registrar.clicked.connect(self.registrar_notificacion)
        boton_buscar = QPushButton("Buscar por paciente")
        boton_buscar.clicked.connect(self.buscar_por_paciente)
        boton_marcar = QPushButton("Marcar como enviada")
        boton_marcar.clicked.connect(self.marcar_como_enviada)
        boton_refrescar = QPushButton("Ver todas")
        boton_refrescar.clicked.connect(self.refrescar_datos)
        layout.addWidget(boton_registrar)
        layout.addWidget(boton_buscar)
        layout.addWidget(boton_marcar)
        layout.addWidget(boton_refrescar)

        self.tabla = QTableWidget(0, 6)
        self.tabla.setHorizontalHeaderLabels(
            ["ID", "Documento", "Fecha", "Tipo", "Mensaje", "Estado"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.itemSelectionChanged.connect(self.cargar_desde_tabla)
        layout.addWidget(self.tabla)

    def registrar_notificacion(self):
        notificacion = Notificacion(
            documento_paciente=self.input_documento.text(),
            tipo=self.combo_tipo.currentText(),
            mensaje=self.input_mensaje.toPlainText(),
        )
        exito, mensaje = self.notificacion_controller.registrar_notificacion(notificacion)
        if exito:
            QMessageBox.information(self, "Notificaciones", mensaje)
            self.input_mensaje.clear()
            self.refrescar_datos()
            return
        QMessageBox.warning(self, "Notificaciones", mensaje)

    def buscar_por_paciente(self):
        documento = self.input_documento.text().strip()
        if not documento:
            QMessageBox.warning(self, "Notificaciones", "Ingresa un documento para filtrar.")
            return
        self._cargar_tabla(self.notificacion_controller.buscar_por_paciente(documento))

    def marcar_como_enviada(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Notificaciones", "Selecciona una notificación.")
            return
        id_notificacion = self.tabla.item(fila, 0).text()
        exito, mensaje = self.notificacion_controller.cambiar_estado(id_notificacion, "Enviada")
        if exito:
            QMessageBox.information(self, "Notificaciones", mensaje)
            self.refrescar_datos()
            return
        QMessageBox.warning(self, "Notificaciones", mensaje)

    def cargar_desde_tabla(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            return
        self.input_documento.setText(self.tabla.item(fila, 1).text())
        self.input_mensaje.setPlainText(self.tabla.item(fila, 4).text())
        self.combo_tipo.setCurrentText(self.tabla.item(fila, 3).text())

    def _cargar_tabla(self, registros):
        self.tabla.setRowCount(len(registros))
        for fila, notificacion in enumerate(registros):
            self.tabla.setItem(fila, 0, QTableWidgetItem(notificacion.get("id_notificacion", "")))
            self.tabla.setItem(fila, 1, QTableWidgetItem(notificacion.get("documento_paciente", "")))
            self.tabla.setItem(fila, 2, QTableWidgetItem(notificacion.get("fecha_creacion", "")))
            self.tabla.setItem(fila, 3, QTableWidgetItem(notificacion.get("tipo", "")))
            self.tabla.setItem(fila, 4, QTableWidgetItem(notificacion.get("mensaje", "")))
            self.tabla.setItem(fila, 5, QTableWidgetItem(notificacion.get("estado", "")))

    def refrescar_datos(self):
        self._cargar_tabla(self.notificacion_controller.listar_notificaciones())
