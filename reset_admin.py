"""
QR Access Control PRO - Reset Admin Password
Usage: python reset_admin.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web_panel.models import user as user_model


def main():
    print("\n🔐 QR Access Control PRO - Reset Admin Password\n")

    admin = user_model.get_by_email('admin@qraccess.com')
    if not admin:
        print("❌ No se encontró el usuario admin (admin@qraccess.com)")
        print("   Se creará uno nuevo...")
        user_model.create_user('Administrador', 'admin@qraccess.com', 'admin123', 'admin')
        print("✅ Admin creado: admin@qraccess.com / admin123")
        return

    new_pass = input("Nueva contraseña para admin (Enter = admin123): ").strip()
    if not new_pass:
        new_pass = 'admin123'

    user_model.update_password(admin['id'], new_pass)
    print(f"✅ Contraseña actualizada para admin@qraccess.com")


if __name__ == '__main__':
    main()
