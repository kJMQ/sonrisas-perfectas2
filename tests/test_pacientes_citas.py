import shutil
import unittest
import uuid
from pathlib import Path

from controladores.cita_controller import CitaController
from controladores.paciente_controller import PacienteController
from modelos.cita import Cita
from modelos.paciente import Paciente


class BasePruebaAislada(unittest.TestCase):
    def setUp(self):
        base = Path(__file__).resolve().parents[1] / ".tmp_test_runs"
        base.mkdir(exist_ok=True)
        self.temp_dir = base / f"run_{uuid.uuid4().hex[:8]}"
        self.temp_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class PacientesCitasTestCase(BasePruebaAislada):
    def setUp(self):
        super().setUp()
        self.paciente_controller = PacienteController(self.temp_dir / "pacientes.json")
        self.cita_controller = CitaController(
            self.temp_dir / "citas.json",
            paciente_controller=self.paciente_controller,
        )

    def test_documento_unico_y_actualizacion(self):
        exito, _ = self.paciente_controller.registrar_paciente(
            Paciente("1001", "Laura Díaz", "3010000000", "laura@example.com", "Calle 5")
        )
        self.assertTrue(exito)

        exito, mensaje = self.paciente_controller.registrar_paciente(
            Paciente("1001", "Laura Duplicada", "3011111111")
        )
        self.assertFalse(exito)
        self.assertIn("Ya existe", mensaje)

        exito, mensaje = self.paciente_controller.actualizar_paciente(
            "1001",
            {
                "documento": "1001",
                "nombre": "Laura Díaz Actualizada",
                "telefono": "3022222222",
                "correo": "laura.actualizada@example.com",
                "direccion": "Carrera 20",
            },
        )
        self.assertTrue(exito)
        paciente = self.paciente_controller.buscar_por_documento("1001")
        self.assertEqual(paciente["nombre"], "Laura Díaz Actualizada")

    def test_cita_requiere_paciente_y_evita_cruce(self):
        exito, mensaje = self.cita_controller.agendar_cita(
            Cita("9999", "2026-07-10", motivo="Valoración", odontologo="Dr. Sofia", hora="09:00")
        )
        self.assertFalse(exito)
        self.assertIn("no está registrado", mensaje)

        self.paciente_controller.registrar_paciente(
            Paciente("2002", "Carlos Ruiz", "3002002002")
        )
        self.paciente_controller.registrar_paciente(
            Paciente("2003", "Ana Torres", "3003003003")
        )

        exito, _ = self.cita_controller.agendar_cita(
            Cita(
                "2002",
                "2026-07-10",
                motivo="Limpieza",
                odontologo="Dr. Sofia",
                hora="09:00",
                nombre_paciente="Carlos Ruiz",
            )
        )
        self.assertTrue(exito)

        exito, mensaje = self.cita_controller.agendar_cita(
            Cita(
                "2003",
                "2026-07-10",
                motivo="Control",
                odontologo="Dr. Sofia",
                hora="09:00",
                nombre_paciente="Ana Torres",
            )
        )
        self.assertFalse(exito)
        self.assertIn("odontólogo", mensaje.lower())
