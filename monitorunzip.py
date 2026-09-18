#!/usr/bin/env python3

import os
import sys
import time
import zipfile


def format_time(seconds):
    if seconds < 0 or seconds == float("inf"):
        return "--"

    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours:
        return f"{hours}h {minutes:02d}m"
    if minutes:
        return f"{minutes}m {seconds:02d}s"

    return f"{seconds}s"


def find_largest_file(zip_path):
    with zipfile.ZipFile(zip_path) as z:
        files = [info for info in z.infolist() if not info.is_dir()]

        if not files:
            raise RuntimeError("El ZIP no contiene archivos.")

        return max(files, key=lambda info: info.file_size)


def monitor(zip_path):
    print(f"Analizando: {zip_path}")

    info = find_largest_file(zip_path)

    filename = info.filename
    total_size = info.file_size

    print(f"Archivo: {filename}")
    print(f"Tamaño total: {total_size / 1e9:.2f} GB")
    print()

    start_time = time.time()

    while True:
        if os.path.exists(filename):
            current_size = os.path.getsize(filename)
        else:
            current_size = 0

        elapsed = time.time() - start_time

        speed = current_size / elapsed if elapsed > 0 else 0

        if speed > 0:
            remaining = (total_size - current_size) / speed
        else:
            remaining = float("inf")

        percentage = (
            current_size / total_size * 100
            if total_size > 0
            else 100
        )

        print(
            f"\r"
            f"{percentage:6.2f}% — "
            f"{current_size / 1e9:.2f}/{total_size / 1e9:.2f} GB — "
            f"{speed / 1e6:.1f} MB/s — "
            f"faltan ~{format_time(remaining)}",
            end="",
            flush=True,
        )

        if current_size >= total_size:
            print("\n\n¡Descompresión terminada!")
            break

        time.sleep(1)


def main():
    if len(sys.argv) != 2:
        print(f"Uso: {sys.argv[0]} archivo.zip")
        sys.exit(1)

    zip_path = sys.argv[1]

    if not os.path.isfile(zip_path):
        print(f"Error: no existe el archivo '{zip_path}'")
        sys.exit(1)

    if not zipfile.is_zipfile(zip_path):
        print(f"Error: '{zip_path}' no parece ser un ZIP válido.")
        sys.exit(1)

    try:
        monitor(zip_path)
    except KeyboardInterrupt:
        print("\n\nMonitor detenido.")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
