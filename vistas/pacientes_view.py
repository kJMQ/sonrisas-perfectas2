from __future__ import annotations

from PySide6.QtWidgets import (
    QAbstractItemView,
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
    QVBoxLayout,
    QWidget,
)

from modelos.paciente import Paciente


class PacientesView(QWidget):
    def __init__(self, paciente_controller, on_change=None, parent=None):
        super().__init__(parent)
        self.paciente_controller = paciente_controller
        self.on_change = on_change
        self._construir_ui()
        self.refrescar_datos()

    def _construir_ui(self):
        layout = QVBoxLayout(self)

        grupo_formulario = QGroupBox("Gestión de pacientes")
        form_layout = QFormLayout(grupo_formulario)

        self.input_documento = QLineEdit()
        self.input_nombre = QLineEdit()
        self.input_telefono = QLineEdit()
        self.input_correo = QLineEdit()
        self.input_direccion = QLineEdit()

        form_layout.addRow("Documento:", self.input_documento)
        form_layout.addRow("Nombre:", self.input_nombre)
        form_layout.addRow("Teléfono:", self.input_telefono)
        form_layout.addRow("Correo:", self.input_correo)
        form_layout.addRow("Dirección:", self.input_direccion)

        botones = QHBoxLayout()
        boton_registrar = QPushButton("Registrar")
        boton_buscar = QPushButton("Buscar por documento")
        boton_actualizar = QPushButton("Actualizar")
        boton_limpiar = QPushButton("Limpiar")

        boton_registrar.clicked.connect(self.registrar_paciente)
        boton_buscar.clicked.connect(self.buscar_paciente)
        boton_actualizar.clicked.connect(self.actualizar_paciente)
        boton_limpiar.clicked.connect(self.limpiar_campos)

        botones.addWidget(boton_registrar)
        botones.addWidget(boton_buscar)
        botones.addWidget(boton_actualizar)
        botones.addWidget(boton_limpiar)

        layout.addWidget(grupo_formulario)
        layout.addLayout(botones)

        self.etiqueta_resultado = QLabel("")
        layout.addWidget(self.etiqueta_resultado)

        self.tabla = QTableWidget(0, 6)
        self.tabla.setHorizontalHeaderLabels(
            ["Documento", "Nombre", "Teléfono", "Correo", "Dirección", "Historiales"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.itemSelectionChanged.connect(self.cargar_desde_tabla)
        layout.addWidget(self.tabla)

    def _paciente_desde_formulario(self):
        return Paciente(
            documento=self.input_documento.text(),
            nombre=self.input_nombre.text(),
            telefono=self.input_telefono.text(),
            correo=self.input_correo.text(),
            direccion=self.input_direccion.text(),
        )

    def registrar_paciente(self):
        exito, mensaje = self.paciente_controller.registrar_paciente(self._paciente_desde_formulario())
        if exito:
            QMessageBox.information(self, "Paciente", mensaje)
            self.limpiar_campos()
            self.refrescar_datos()
            if self.on_change:
                self.on_change()
            return
        QMessageBox.warning(self, "Paciente", mensaje)

    def buscar_paciente(self):
        documento = self.input_documento.text().strip()
        paciente = self.paciente_controller.buscar_por_documento(documento)
        if not paciente:
            QMessageBox.warning(self, "Búsqueda", "No se encontró un paciente con ese documento.")
            return
        self._cargar_paciente_en_formulario(paciente)
        self.etiqueta_resultado.setText(f"Paciente encontrado: {paciente.get('nombre')}")

    def actualizar_paciente(self):
        documento = self.input_documento.text().strip()
        exito, mensaje = self.paciente_controller.actualizar_paciente(
            documento,
            self._paciente_desde_formulario().to_dict(),
        )
        if exito:
            QMessageBox.information(self, "Paciente", mensaje)
            self.refrescar_datos()
            if self.on_change:
                self.on_change()
            return
        QMessageBox.warning(self, "Paciente", mensaje)

    def _cargar_paciente_en_formulario(self, paciente):
        self.input_documento.setText(paciente.get("documento", ""))
        self.input_nombre.setText(paciente.get("nombre", ""))
        self.input_telefono.setText(paciente.get("telefono", ""))
        self.input_correo.setText(paciente.get("correo", ""))
        self.input_direccion.setText(paciente.get("direccion", ""))

    def cargar_desde_tabla(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            return
        paciente = {
            "documento": self.tabla.item(fila, 0).text(),
            "nombre": self.tabla.item(fila, 1).text(),
            "telefono": self.tabla.item(fila, 2).text(),
            "correo": self.tabla.item(fila, 3).text(),
            "direccion": self.tabla.item(fila, 4).text(),
        }
        self._cargar_paciente_en_formulario(paciente)

    def limpiar_campos(self):
        self.input_documento.clear()
        self.input_nombre.clear()
        self.input_telefono.clear()
        self.input_correo.clear()
        self.input_direccion.clear()
        self.etiqueta_resultado.clear()

    def refrescar_datos(self):
        pacientes = self.paciente_controller.listar_pacientes()
        self.tabla.setRowCount(len(pacientes))
        for fila, paciente in enumerate(pacientes):
            self.tabla.setItem(fila, 0, QTableWidgetItem(paciente.get("documento", "")))
            self.tabla.setItem(fila, 1, QTableWidgetItem(paciente.get("nombre", "")))
            self.tabla.setItem(fila, 2, QTableWidgetItem(paciente.get("telefono", "")))
            self.tabla.setItem(fila, 3, QTableWidgetItem(paciente.get("correo", "")))
            self.tabla.setItem(fila, 4, QTableWidgetItem(paciente.get("direccion", "")))
            self.tabla.setItem(
                fila,
                5,
                QTableWidgetItem(str(len(paciente.get("historial", [])))),
            )
