from __future__ import annotations

import shutil
from datetime import datetime

from .json_manager import JsonManager


class BackupManager:
    @staticmethod
    def crear_respaldo():
        data_dir = JsonManager.DATA_DIR
        destino = data_dir / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        destino.mkdir(parents=True, exist_ok=True)

        total = 0
        for archivo_json in data_dir.glob("*.json"):
            shutil.copy2(archivo_json, destino / archivo_json.name)
            total += 1

        return {
            "destino": str(destino),
            "archivos": total,
        }
