"""
QR Access Control PRO - Physical Scanner Module
Uses OpenCV and pyzbar to capture and validate QR codes from a camera feed.
Validates against MySQL database and logs access attempts.
"""
import sys
import os
import time
from datetime import datetime

# Add project root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import cv2
import numpy as np
from pyzbar import pyzbar

from config.settings import config
from web_panel.models import user as user_model, access_log


# ── Configuration ────────────────────────
CAMERA_INDEX = 0
SCANNER_ID = 'main'
SCAN_COOLDOWN = 3  # seconds between same QR scans
WINDOW_NAME = 'QR Access Control PRO - Scanner'

# Colors (BGR)
COLOR_SUCCESS = (128, 222, 74)   # Green
COLOR_DENIED = (113, 113, 248)   # Red
COLOR_INFO = (250, 165, 96)      # Blue
COLOR_WHITE = (255, 255, 255)
COLOR_BG = (26, 26, 42)


def draw_overlay(frame, text, color, user_name="", timestamp=""):
    """Draw result overlay on frame."""
    h, w = frame.shape[:2]

    # Bottom bar
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, h - 100), (w, h), COLOR_BG, -1)
    frame = cv2.addWeighted(overlay, 0.85, frame, 0.15, 0)

    # Status text
    cv2.putText(frame, text, (20, h - 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)

    if user_name:
        cv2.putText(frame, user_name, (20, h - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_WHITE, 1)

    if timestamp:
        cv2.putText(frame, timestamp, (w - 200, h - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_INFO, 1)

    # Top bar with title
    cv2.rectangle(frame, (0, 0), (w, 45), COLOR_BG, -1)
    cv2.putText(frame, "QR Access Control PRO", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_INFO, 2)

    return frame


def validate_qr(qr_data):
    """Validate a QR code against the database."""
    try:
        user = user_model.get_by_qr(qr_data)

        if user and user['activo']:
            # Check expiration
            if user.get('fecha_expiracion') and user['fecha_expiracion'] < datetime.now():
                access_log.create_log(qr_data, 'denegado', user['id'])
                return 'denegado', user['nombre'], 'QR expirado'

            access_log.create_log(qr_data, 'permitido', user['id'])
            return 'permitido', user['nombre'], ''

        elif user and not user['activo']:
            access_log.create_log(qr_data, 'denegado', user['id'])
            return 'denegado', user['nombre'], 'Desactivado'

        else:
            access_log.create_log(qr_data, 'denegado')
            return 'denegado', 'Desconocido', 'No registrado'

    except Exception as e:
        print(f"[ERROR] Error validando QR: {e}")
        return 'error', '', str(e)


def main():
    """Main scanner loop."""
    print("\n" + "=" * 50)
    print("  🔐 QR ACCESS CONTROL PRO - SCANNER")
    print("=" * 50)
    print(f"  📷 Cámara: {CAMERA_INDEX}")
    print(f"  💾 BD: {config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}")
    print(f"  🔄 Cooldown: {SCAN_COOLDOWN}s")
    print(f"  ⌨️  Controles: 'q' = Salir | 's' = Captura")
    print("=" * 50 + "\n")

    # Open camera
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"[ERROR] No se pudo abrir la cámara {CAMERA_INDEX}")
        print("  Prueba con otro índice: python scanner_fisico.py [0|1|2]")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("[INFO] Cámara abierta. Esperando códigos QR...\n")

    last_scanned = {}
    last_result = ("Esperando QR...", COLOR_INFO, "", "")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[ERROR] No se pudo leer frame de la cámara")
                break

            # Decode QR codes
            decoded = pyzbar.decode(frame)

            for qr in decoded:
                qr_data = qr.data.decode('utf-8')
                now = time.time()

                # Draw QR bounding box
                points = qr.polygon
                if len(points) == 4:
                    pts = np.array([[p.x, p.y] for p in points], np.int32)
                    cv2.polylines(frame, [pts], True, COLOR_INFO, 2)

                # Cooldown check
                if qr_data in last_scanned and (now - last_scanned[qr_data]) < SCAN_COOLDOWN:
                    continue

                last_scanned[qr_data] = now
                timestamp = datetime.now().strftime('%H:%M:%S')

                # Validate
                resultado, nombre, detalle = validate_qr(qr_data)

                if resultado == 'permitido':
                    color = COLOR_SUCCESS
                    status = "ACCESO PERMITIDO"
                    print(f"  ✅ [{timestamp}] PERMITIDO - {nombre}")
                else:
                    color = COLOR_DENIED
                    status = "ACCESO DENEGADO"
                    print(f"  ❌ [{timestamp}] DENEGADO - {nombre} ({detalle})")

                last_result = (status, color, nombre, timestamp)

            # Draw overlay
            display_frame = draw_overlay(frame, last_result[0], last_result[1],
                                         last_result[2], last_result[3])

            cv2.imshow(WINDOW_NAME, display_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\n[INFO] Scanner detenido por el usuario.")
                break
            elif key == ord('s'):
                filename = f"captura_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                cv2.imwrite(filename, frame)
                print(f"  📸 Captura guardada: {filename}")

    except KeyboardInterrupt:
        print("\n[INFO] Scanner detenido (Ctrl+C).")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("[INFO] Recursos liberados. Hasta luego!")


if __name__ == '__main__':
    # Allow camera index as argument
    if len(sys.argv) > 1:
        try:
            CAMERA_INDEX = int(sys.argv[1])
        except ValueError:
            pass
    main()
