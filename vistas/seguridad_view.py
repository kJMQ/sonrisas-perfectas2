from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from modelos.usuario import Usuario
from utils.backup_manager import BackupManager


class SeguridadView(QWidget):
    def __init__(self, usuario_controller, usuario_actual, on_change=None, parent=None):
        super().__init__(parent)
        self.usuario_controller = usuario_controller
        self.usuario_actual = usuario_actual
        self.on_change = on_change
        self._construir_ui()
        self.refrescar_datos()

    def _construir_ui(self):
        layout = QVBoxLayout(self)

        grupo = QGroupBox("Usuarios y roles")
        form_layout = QFormLayout(grupo)
        self.input_username = QLineEdit()
        self.input_password = QLineEdit()
        self.input_nombre = QLineEdit()
        self.combo_rol = QComboBox()
        self.combo_rol.addItems([rol.get("nombre") for rol in self.usuario_controller.listar_roles()])
        self.check_activo = QCheckBox("Usuario activo")
        self.check_activo.setChecked(True)
        self.check_mfa = QCheckBox("Requiere MFA simulado")
        form_layout.addRow("Usuario:", self.input_username)
        form_layout.addRow("Contraseña:", self.input_password)
        form_layout.addRow("Nombre:", self.input_nombre)
        form_layout.addRow("Rol:", self.combo_rol)
        form_layout.addRow("", self.check_activo)
        form_layout.addRow("", self.check_mfa)
        layout.addWidget(grupo)

        botones = QHBoxLayout()
        boton_registrar = QPushButton("Registrar usuario")
        boton_backup = QPushButton("Crear backup JSON")
        boton_refrescar = QPushButton("Refrescar seguridad")
        boton_registrar.clicked.connect(self.registrar_usuario)
        boton_backup.clicked.connect(self.crear_backup)
        boton_refrescar.clicked.connect(self.refrescar_datos)
        botones.addWidget(boton_registrar)
        botones.addWidget(boton_backup)
        botones.addWidget(boton_refrescar)
        layout.addLayout(botones)

        self.tabla_usuarios = QTableWidget(0, 5)
        self.tabla_usuarios.setHorizontalHeaderLabels(
            ["Usuario", "Nombre", "Rol", "Activo", "MFA"]
        )
        self.tabla_usuarios.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla_usuarios)

        self.tabla_roles = QTableWidget(0, 3)
        self.tabla_roles.setHorizontalHeaderLabels(["Rol", "Permisos", "Descripción"])
        self.tabla_roles.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla_roles)

        self.tabla_bitacora = QTableWidget(0, 6)
        self.tabla_bitacora.setHorizontalHeaderLabels(
            ["Fecha", "Usuario", "Rol", "Acción", "Detalle", "Resultado"]
        )
        self.tabla_bitacora.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla_bitacora)

    def registrar_usuario(self):
        usuario = Usuario(
            username=self.input_username.text(),
            password=self.input_password.text(),
            nombre=self.input_nombre.text(),
            rol=self.combo_rol.currentText(),
            activo=self.check_activo.isChecked(),
            mfa_habilitado=self.check_mfa.isChecked(),
        )
        exito, mensaje = self.usuario_controller.registrar_usuario(usuario)
        if exito:
            self.usuario_controller.registrar_bitacora(
                self.usuario_actual,
                "registro_usuario",
                f"Se registró el usuario {usuario.username}.",
                "OK",
            )
            QMessageBox.information(self, "Seguridad", mensaje)
            self.refrescar_datos()
            self.input_username.clear()
            self.input_password.clear()
            self.input_nombre.clear()
            if self.on_change:
                self.on_change()
            return
        QMessageBox.warning(self, "Seguridad", mensaje)

    def crear_backup(self):
        respaldo = BackupManager.crear_respaldo()
        self.usuario_controller.registrar_bitacora(
            self.usuario_actual,
            "backup",
            f"Backup generado en {respaldo['destino']}.",
            "OK",
        )
        QMessageBox.information(
            self,
            "Seguridad",
            f"Backup creado con {respaldo['archivos']} archivos en:\n{respaldo['destino']}",
        )
        self.refrescar_datos()

    def refrescar_datos(self):
        usuarios = self.usuario_controller.listar_usuarios()
        self.tabla_usuarios.setRowCount(len(usuarios))
        for fila, usuario in enumerate(usuarios):
            self.tabla_usuarios.setItem(fila, 0, QTableWidgetItem(usuario.get("username", "")))
            self.tabla_usuarios.setItem(fila, 1, QTableWidgetItem(usuario.get("nombre", "")))
            self.tabla_usuarios.setItem(fila, 2, QTableWidgetItem(usuario.get("rol", "")))
            self.tabla_usuarios.setItem(fila, 3, QTableWidgetItem(str(usuario.get("activo", True))))
            self.tabla_usuarios.setItem(
                fila, 4, QTableWidgetItem(str(usuario.get("mfa_habilitado", False)))
            )

        roles = self.usuario_controller.listar_roles()
        self.tabla_roles.setRowCount(len(roles))
        for fila, rol in enumerate(roles):
            self.tabla_roles.setItem(fila, 0, QTableWidgetItem(rol.get("nombre", "")))
            self.tabla_roles.setItem(
                fila, 1, QTableWidgetItem(", ".join(rol.get("permisos", [])))
            )
            self.tabla_roles.setItem(fila, 2, QTableWidgetItem(rol.get("descripcion", "")))

        bitacora = self.usuario_controller.listar_bitacora()
        self.tabla_bitacora.setRowCount(len(bitacora))
        for fila, evento in enumerate(bitacora):
            self.tabla_bitacora.setItem(fila, 0, QTableWidgetItem(evento.get("fecha", "")))
            self.tabla_bitacora.setItem(fila, 1, QTableWidgetItem(evento.get("usuario", "")))
            self.tabla_bitacora.setItem(fila, 2, QTableWidgetItem(evento.get("rol", "")))
            self.tabla_bitacora.setItem(fila, 3, QTableWidgetItem(evento.get("accion", "")))
            self.tabla_bitacora.setItem(fila, 4, QTableWidgetItem(evento.get("detalle", "")))
            self.tabla_bitacora.setItem(fila, 5, QTableWidgetItem(evento.get("resultado", "")))
