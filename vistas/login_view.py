from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from controladores.auth_controller import AuthController


class LoginView(QDialog):
    def __init__(self, auth_controller=None, parent=None):
        super().__init__(parent)
        self.auth_controller = auth_controller or AuthController()
        self.usuario_autenticado = None
        self.setWindowTitle("Inicio de sesión - Sonrisa Perfecta")
        self.resize(420, 260)
        self._construir_ui()

    def _construir_ui(self):
        layout = QVBoxLayout(self)

        titulo = QLabel("Sistema de Gestión Clínica Dental Sonrisa Perfecta")
        titulo.setWordWrap(True)
        layout.addWidget(titulo)

        ayuda = QLabel(
            "Usuarios demo: admin/admin123, recepcion/recepcion123, "
            "doctor/doctor123, gerencia/gerencia123. "
            "Si el rol tiene MFA, usa el código 123456."
        )
        ayuda.setWordWrap(True)
        layout.addWidget(ayuda)

        formulario = QFormLayout()
        self.input_usuario = QLineEdit()
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_mfa = QLineEdit()
        self.input_mfa.setPlaceholderText("Solo si el rol usa MFA")

        formulario.addRow("Usuario:", self.input_usuario)
        formulario.addRow("Contraseña:", self.input_password)
        formulario.addRow("Código MFA:", self.input_mfa)
        layout.addLayout(formulario)

        self.boton_ingresar = QPushButton("Ingresar")
        self.boton_ingresar.clicked.connect(self.procesar_login)
        layout.addWidget(self.boton_ingresar)

    def procesar_login(self):
        exito, mensaje, usuario = self.auth_controller.iniciar_sesion(
            self.input_usuario.text(),
            self.input_password.text(),
            self.input_mfa.text(),
        )
        if not exito:
            QMessageBox.warning(self, "Acceso denegado", mensaje)
            return

        self.usuario_autenticado = usuario
        QMessageBox.information(self, "Acceso concedido", mensaje)
        self.accept()
