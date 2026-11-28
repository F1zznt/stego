"""Реализация режима 2: На выход подаётся картинка и алгоритм на выход текст"""
from PySide6.QtWidgets import QComboBox
from pathlib import Path
from imagestego import lsb_extract_message
from imagestego.stego_tools import run_stego_batch

def get_data(algoBox: QComboBox) -> str:
    algo = algoBox.currentText()
    return algo

def detect_type(file_path: str) -> str:
    with open(file_path, "rb") as file:
        header = file.read(12)

    if header.startswith(b"\x89PNG\r\n\x1A\n"):
        return "IMG"

    elif header.startswith(b"BM"):
        return "IMG"

    elif header.startswith((b"II*\x00", b"MM\x00*")):
        return "IMG"

    elif header.startswith(b"RIFF") and header[8:12] == b"WAVE":
        return "WAV"

    return "Расширение файла не поддерживается, мы работаем только с png, bmp, tiff, wav"

def destego(algo: str, file_path: str, ext: str) -> str:
    algorithms = {
        "LSB": "lsb",
        "LSBE": "lsb_edge",
        "DCT": "dct",
        "DWT": "dwt",
        "PVD": "pvd",
        "SS": "spread_spectrum",
        "ALSB": "audio_lsb"
    }

    if not Path(file_path).is_file():
        return "Файл не загружен"

    if ext == "IMG" and algo == "ALSB":
        return "ALSB предназначен для WAV"

    if ext == "WAV" and algo != "ALSB":
        return f"{algo} предназначен для изображений"

    if algo == "LSB":
        result = lsb_extract_message(file_path)
        return result["message"]

    name = Path(file_path).name
    if ext == "IMG":
        rows = run_stego_batch(
            [{
                "name": name,
                "path": file_path
            }],
            "./output",
            method=algorithms[algo],
            operation="extract",
            settings={"seed": 42}
        )

        if not rows:
            return "Нет текста"

        return str(rows[0])