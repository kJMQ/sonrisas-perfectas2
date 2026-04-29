from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
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


class ReportesView(QWidget):
    def __init__(self, reporte_controller, parent=None):
        super().__init__(parent)
        self.reporte_controller = reporte_controller
        self._construir_ui()

    def _construir_ui(self):
        layout = QVBoxLayout(self)

        formulario = QFormLayout()
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(
            [
                "Pacientes registrados",
                "Citas por rango",
                "Reporte clínico por paciente",
                "Reporte financiero por rango",
            ]
        )
        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setDate(QDate.currentDate().addMonths(-1))
        self.fecha_inicio.setDisplayFormat("yyyy-MM-dd")
        self.fecha_inicio.setCalendarPopup(True)
        self.fecha_fin = QDateEdit()
        self.fecha_fin.setDate(QDate.currentDate())
        self.fecha_fin.setDisplayFormat("yyyy-MM-dd")
        self.fecha_fin.setCalendarPopup(True)
        self.input_documento = QLineEdit()

        formulario.addRow("Tipo de reporte:", self.combo_tipo)
        formulario.addRow("Fecha inicio:", self.fecha_inicio)
        formulario.addRow("Fecha fin:", self.fecha_fin)
        formulario.addRow("Documento paciente:", self.input_documento)
        layout.addLayout(formulario)

        boton = QPushButton("Generar reporte")
        boton.clicked.connect(self.generar_reporte)
        layout.addWidget(boton)

        self.area_resumen = QTextEdit()
        self.area_resumen.setReadOnly(True)
        layout.addWidget(self.area_resumen)

        self.tabla = QTableWidget(0, 0)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla)

    def generar_reporte(self):
        tipo = self.combo_tipo.currentText()
        fecha_inicio = self.fecha_inicio.date().toString("yyyy-MM-dd")
        fecha_fin = self.fecha_fin.date().toString("yyyy-MM-dd")
        documento = self.input_documento.text().strip()

        if tipo == "Pacientes registrados":
            reporte = self.reporte_controller.reporte_pacientes()
        elif tipo == "Citas por rango":
            reporte = self.reporte_controller.reporte_citas_por_rango(fecha_inicio, fecha_fin)
        elif tipo == "Reporte clínico por paciente":
            if not documento:
                QMessageBox.warning(self, "Reportes", "Ingresa el documento del paciente.")
                return
            reporte = self.reporte_controller.reporte_clinico_por_paciente(documento)
        else:
            reporte = self.reporte_controller.reporte_financiero_por_rango(fecha_inicio, fecha_fin)

        self.area_resumen.setPlainText(f"{reporte['titulo']}\n\n{reporte['resumen']}")
        self.tabla.setColumnCount(len(reporte["columnas"]))
        self.tabla.setHorizontalHeaderLabels(reporte["columnas"])
        self.tabla.setRowCount(len(reporte["filas"]))
        for fila, valores in enumerate(reporte["filas"]):
            for columna, valor in enumerate(valores):
                self.tabla.setItem(fila, columna, QTableWidgetItem(str(valor)))

    def refrescar_datos(self):
        return
