from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path


class JsonManager:
    """Centraliza lectura y escritura segura de archivos JSON."""

    BASE_DIR = Path(__file__).resolve().parents[1]
    DATA_DIR = BASE_DIR / "data"

    @classmethod
    def resolver_ruta(cls, nombre_archivo):
        ruta = Path(nombre_archivo)
        if not ruta.is_absolute():
            if ruta.parts and ruta.parts[0] == "data":
                ruta = cls.BASE_DIR / ruta
            else:
                ruta = cls.DATA_DIR / ruta
        ruta.parent.mkdir(parents=True, exist_ok=True)
        return ruta

    @classmethod
    def leer(cls, nombre_archivo, default=None):
        valor_por_defecto = [] if default is None else deepcopy(default)
        ruta = cls.resolver_ruta(nombre_archivo)

        if not ruta.exists():
            cls.guardar(ruta, valor_por_defecto)
            return deepcopy(valor_por_defecto)

        try:
            with ruta.open("r", encoding="utf-8") as archivo:
                contenido = json.load(archivo)
                return contenido
        except (json.JSONDecodeError, FileNotFoundError, OSError):
            cls.guardar(ruta, valor_por_defecto)
            return deepcopy(valor_por_defecto)

    @classmethod
    def guardar(cls, nombre_archivo, data):
        ruta = cls.resolver_ruta(nombre_archivo)
        with ruta.open("w", encoding="utf-8") as archivo:
            json.dump(data, archivo, indent=4, ensure_ascii=False)

    @classmethod
    def anexar(cls, nombre_archivo, item):
        registros = cls.leer(nombre_archivo, [])
        registros.append(item)
        cls.guardar(nombre_archivo, registros)
