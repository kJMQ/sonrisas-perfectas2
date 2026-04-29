from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
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
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from modelos.historial_medico import HistorialMedico


class HistorialView(QWidget):
    def __init__(
        self,
        historial_controller,
        paciente_controller,
        usuario_controller,
        on_change=None,
        parent=None,
    ):
        super().__init__(parent)
        self.historial_controller = historial_controller
        self.paciente_controller = paciente_controller
        self.usuario_controller = usuario_controller
        self.on_change = on_change
        self._construir_ui()

    def _odontologos(self):
        lista = [
            usuario.get("nombre")
            for usuario in self.usuario_controller.listar_usuarios()
            if usuario.get("rol") == "odontologo"
        ]
        return lista or ["Odontólogo general"]

    def _construir_ui(self):
        layout = QVBoxLayout(self)

        grupo = QGroupBox("Historial clínico")
        form_layout = QFormLayout(grupo)

        self.input_documento = QLineEdit()
        self.label_paciente = QLabel("Sin paciente cargado")
        self.combo_odontologo = QComboBox()
        self.combo_odontologo.addItems(self._odontologos())
        self.input_diagnostico = QLineEdit()
        self.input_tratamiento = QLineEdit()
        self.input_observaciones = QTextEdit()

        form_layout.addRow("Documento paciente:", self.input_documento)
        form_layout.addRow("Paciente:", self.label_paciente)
        form_layout.addRow("Odontólogo:", self.combo_odontologo)
        form_layout.addRow("Diagnóstico:", self.input_diagnostico)
        form_layout.addRow("Tratamiento:", self.input_tratamiento)
        form_layout.addRow("Observaciones:", self.input_observaciones)
        layout.addWidget(grupo)

        botones = QHBoxLayout()
        boton_guardar = QPushButton("Registrar entrada")
        boton_consultar = QPushButton("Consultar historial")
        boton_limpiar = QPushButton("Limpiar")

        boton_guardar.clicked.connect(self.registrar_entrada)
        boton_consultar.clicked.connect(self.consultar_historial)
        boton_limpiar.clicked.connect(self.limpiar)

        botones.addWidget(boton_guardar)
        botones.addWidget(boton_consultar)
        botones.addWidget(boton_limpiar)
        layout.addLayout(botones)

        self.tabla = QTableWidget(0, 5)
        self.tabla.setHorizontalHeaderLabels(
            ["Fecha", "Odontólogo", "Diagnóstico", "Tratamiento", "Observaciones"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla)

    def _actualizar_paciente_label(self):
        paciente = self.paciente_controller.buscar_por_documento(self.input_documento.text().strip())
        self.label_paciente.setText(paciente.get("nombre", "Paciente no encontrado") if paciente else "Paciente no encontrado")
        return paciente

    def registrar_entrada(self):
        paciente = self._actualizar_paciente_label()
        if not paciente:
            QMessageBox.warning(self, "Historial", "El paciente no existe.")
            return

        registro = HistorialMedico(
            documento_paciente=self.input_documento.text(),
            odontologo=self.combo_odontologo.currentText(),
            diagnostico=self.input_diagnostico.text(),
            tratamiento=self.input_tratamiento.text(),
            observaciones=self.input_observaciones.toPlainText(),
        )
        exito, mensaje = self.historial_controller.registrar_entrada(registro)
        if exito:
            QMessageBox.information(self, "Historial", mensaje)
            self.consultar_historial()
            self.input_diagnostico.clear()
            self.input_tratamiento.clear()
            self.input_observaciones.clear()
            if self.on_change:
                self.on_change()
            return
        QMessageBox.warning(self, "Historial", mensaje)

    def consultar_historial(self):
        paciente = self._actualizar_paciente_label()
        if not paciente:
            QMessageBox.warning(self, "Historial", "No se encontró el paciente.")
            return
        registros = self.historial_controller.consultar_por_paciente(self.input_documento.text().strip())
        self.tabla.setRowCount(len(registros))
        for fila, registro in enumerate(registros):
            self.tabla.setItem(fila, 0, QTableWidgetItem(registro.get("fecha", "")))
            self.tabla.setItem(fila, 1, QTableWidgetItem(registro.get("odontologo", "")))
            self.tabla.setItem(fila, 2, QTableWidgetItem(registro.get("diagnostico", "")))
            self.tabla.setItem(fila, 3, QTableWidgetItem(registro.get("tratamiento", "")))
            self.tabla.setItem(fila, 4, QTableWidgetItem(registro.get("observaciones", "")))

    def limpiar(self):
        self.input_documento.clear()
        self.label_paciente.setText("Sin paciente cargado")
        self.input_diagnostico.clear()
        self.input_tratamiento.clear()
        self.input_observaciones.clear()
        self.tabla.setRowCount(0)

    def refrescar_datos(self):
        if self.input_documento.text().strip():
            self.consultar_historial()
