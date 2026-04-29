import sys

from PySide6.QtWidgets import QApplication

from controladores.auth_controller import AuthController
from controladores.usuario_controller import UsuarioController
from vistas.login_view import LoginView
from vistas.ventana_principal import VentanaPrincipalClinica


class CoordinadorAplicacion:
    def __init__(self):
        self.usuario_controller = UsuarioController()
        self.auth_controller = AuthController(self.usuario_controller)
        self.ventana_principal = None

    def iniciar(self):
        self.mostrar_login()

    def mostrar_login(self):
        login = LoginView(self.auth_controller)
        if login.exec() != LoginView.Accepted:
            QApplication.quit()
            return
        self.mostrar_principal(login.usuario_autenticado)

    def mostrar_principal(self, usuario):
        self.ventana_principal = VentanaPrincipalClinica(usuario)
        self.ventana_principal.cerrar_sesion_solicitada.connect(self.mostrar_login)
        self.ventana_principal.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    coordinador = CoordinadorAplicacion()
    coordinador.iniciar()
    sys.exit(app.exec())
