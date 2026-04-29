from __future__ import annotations

from PySide6.QtCore import QDate, QTime
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDateEdit,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from modelos.cita import Cita


class CitasView(QWidget):
    def __init__(
        self,
        cita_controller,
        paciente_controller,
        notificacion_controller,
        usuario_controller,
        on_change=None,
        parent=None,
    ):
        super().__init__(parent)
        self.cita_controller = cita_controller
        self.paciente_controller = paciente_controller
        self.notificacion_controller = notificacion_controller
        self.usuario_controller = usuario_controller
        self.on_change = on_change
        self._construir_ui()
        self.refrescar_datos()

    def _obtener_odontologos(self):
        odontologos = [
            usuario.get("nombre")
            for usuario in self.usuario_controller.listar_usuarios()
            if usuario.get("rol") == "odontologo"
        ]
        return odontologos or ["Odontólogo general"]

    def _construir_ui(self):
        layout = QVBoxLayout(self)

        grupo = QGroupBox("Agenda de citas")
        form_layout = QFormLayout(grupo)

        self.input_id = QLineEdit()
        self.input_id.setReadOnly(True)
        self.input_documento = QLineEdit()
        self.label_nombre = QLabel("Paciente no cargado")
        self.fecha = QDateEdit()
        self.fecha.setDate(QDate.currentDate())
        self.fecha.setDisplayFormat("yyyy-MM-dd")
        self.fecha.setCalendarPopup(True)
        self.hora = QTimeEdit()
        self.hora.setTime(QTime.currentTime())
        self.hora.setDisplayFormat("HH:mm")
        self.input_motivo = QLineEdit()
        self.combo_odontologo = QComboBox()
        self.combo_odontologo.addItems(self._obtener_odontologos())
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(["Activa", "Atendida", "Cancelada"])

        form_layout.addRow("ID cita:", self.input_id)
        form_layout.addRow("Documento paciente:", self.input_documento)
        form_layout.addRow("Paciente:", self.label_nombre)
        form_layout.addRow("Fecha:", self.fecha)
        form_layout.addRow("Hora:", self.hora)
        form_layout.addRow("Motivo:", self.input_motivo)
        form_layout.addRow("Odontólogo:", self.combo_odontologo)
        form_layout.addRow("Estado:", self.combo_estado)
        layout.addWidget(grupo)

        botones = QHBoxLayout()
        boton_agendar = QPushButton("Agendar")
        boton_buscar = QPushButton("Buscar por paciente")
        boton_modificar = QPushButton("Modificar")
        boton_cancelar = QPushButton("Cancelar cita")
        boton_limpiar = QPushButton("Limpiar")

        boton_agendar.clicked.connect(self.agendar_cita)
        boton_buscar.clicked.connect(self.buscar_por_paciente)
        boton_modificar.clicked.connect(self.modificar_cita)
        boton_cancelar.clicked.connect(self.cancelar_cita)
        boton_limpiar.clicked.connect(self.limpiar_formulario)

        botones.addWidget(boton_agendar)
        botones.addWidget(boton_buscar)
        botones.addWidget(boton_modificar)
        botones.addWidget(boton_cancelar)
        botones.addWidget(boton_limpiar)
        layout.addLayout(botones)

        self.tabla = QTableWidget(0, 8)
        self.tabla.setHorizontalHeaderLabels(
            ["ID", "Documento", "Paciente", "Fecha", "Hora", "Motivo", "Odontólogo", "Estado"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.itemSelectionChanged.connect(self.cargar_desde_tabla)
        layout.addWidget(self.tabla)

    def _obtener_nombre_paciente(self):
        paciente = self.paciente_controller.buscar_por_documento(self.input_documento.text().strip())
        if paciente:
            self.label_nombre.setText(paciente.get("nombre", ""))
            return paciente.get("nombre", "")
        self.label_nombre.setText("Paciente no encontrado")
        return ""

    def _cita_desde_formulario(self):
        nombre = self._obtener_nombre_paciente()
        return Cita(
            documento_paciente=self.input_documento.text(),
            nombre_paciente=nombre,
            fecha=self.fecha.date().toString("yyyy-MM-dd"),
            hora=self.hora.time().toString("HH:mm"),
            motivo=self.input_motivo.text(),
            odontologo=self.combo_odontologo.currentText(),
            estado=self.combo_estado.currentText(),
            id_cita=self.input_id.text() or None,
        )

    def agendar_cita(self):
        cita = self._cita_desde_formulario()
        exito, mensaje = self.cita_controller.agendar_cita(cita)
        if not exito:
            QMessageBox.warning(self, "Citas", mensaje)
            return

        self.notificacion_controller.crear_confirmacion_cita(cita.to_dict())
        self.notificacion_controller.crear_recordatorio_cita(cita.to_dict())
        QMessageBox.information(self, "Citas", mensaje)
        self.limpiar_formulario()
        self.refrescar_datos()
        if self.on_change:
            self.on_change()

    def buscar_por_paciente(self):
        documento = self.input_documento.text().strip()
        if not documento:
            QMessageBox.warning(self, "Citas", "Ingresa el documento del paciente.")
            return
        citas = self.cita_controller.buscar_por_paciente(documento)
        self.refrescar_datos(citas)
        self._obtener_nombre_paciente()

    def modificar_cita(self):
        id_cita = self.input_id.text().strip()
        if not id_cita:
            QMessageBox.warning(self, "Citas", "Selecciona primero una cita de la tabla.")
            return
        exito, mensaje = self.cita_controller.modificar_cita(id_cita, self._cita_desde_formulario().to_dict())
        if exito:
            QMessageBox.information(self, "Citas", mensaje)
            self.refrescar_datos()
            if self.on_change:
                self.on_change()
            return
        QMessageBox.warning(self, "Citas", mensaje)

    def cancelar_cita(self):
        id_cita = self.input_id.text().strip()
        if not id_cita:
            QMessageBox.warning(self, "Citas", "Selecciona una cita para cancelarla.")
            return
        exito, mensaje = self.cita_controller.cancelar_cita(id_cita)
        if exito:
            QMessageBox.information(self, "Citas", mensaje)
            self.refrescar_datos()
            if self.on_change:
                self.on_change()
            return
        QMessageBox.warning(self, "Citas", mensaje)

    def cargar_desde_tabla(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            return
        self.input_id.setText(self.tabla.item(fila, 0).text())
        self.input_documento.setText(self.tabla.item(fila, 1).text())
        self.label_nombre.setText(self.tabla.item(fila, 2).text())
        self.fecha.setDate(QDate.fromString(self.tabla.item(fila, 3).text(), "yyyy-MM-dd"))
        self.hora.setTime(QTime.fromString(self.tabla.item(fila, 4).text(), "HH:mm"))
        self.input_motivo.setText(self.tabla.item(fila, 5).text())
        self.combo_odontologo.setCurrentText(self.tabla.item(fila, 6).text())
        self.combo_estado.setCurrentText(self.tabla.item(fila, 7).text())

    def limpiar_formulario(self):
        self.input_id.clear()
        self.input_documento.clear()
        self.label_nombre.setText("Paciente no cargado")
        self.fecha.setDate(QDate.currentDate())
        self.hora.setTime(QTime.currentTime())
        self.input_motivo.clear()
        self.combo_estado.setCurrentText("Activa")

    def refrescar_datos(self, citas=None):
        registros = citas if citas is not None else self.cita_controller.listar_todas()
        self.tabla.setRowCount(len(registros))
        for fila, cita in enumerate(registros):
            self.tabla.setItem(fila, 0, QTableWidgetItem(cita.get("id_cita", "")))
            self.tabla.setItem(fila, 1, QTableWidgetItem(cita.get("documento_paciente", "")))
            self.tabla.setItem(fila, 2, QTableWidgetItem(cita.get("nombre_paciente", "")))
            self.tabla.setItem(fila, 3, QTableWidgetItem(cita.get("fecha", "")))
            self.tabla.setItem(fila, 4, QTableWidgetItem(cita.get("hora", "")))
            self.tabla.setItem(fila, 5, QTableWidgetItem(cita.get("motivo", "")))
            self.tabla.setItem(fila, 6, QTableWidgetItem(cita.get("odontologo", "")))
            self.tabla.setItem(fila, 7, QTableWidgetItem(cita.get("estado", "")))
