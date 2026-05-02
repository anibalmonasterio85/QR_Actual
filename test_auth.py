"""
QR Access Control PRO - Authentication Test Script
Tests the authenticate() function directly to verify login will work.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web_panel.models import user as user_model

print("\n=== QR Access PRO - Auth Test ===\n")

# Test all known users
test_cases = [
    ('admin@qraccess.com', 'admin123'),
    ('admin@qraccess.com', 'Admin123!'),
    ('anibalmonas124@gmail.com', 'Admin123!'),
    ('anibalmj090@gmail.com', 'Admin123!'),
]

for correo, password in test_cases:
    user = user_model.get_by_email(correo)
    if not user:
        print(f"  [{correo}] => USER NOT FOUND")
        continue
    
    result = user_model.authenticate(correo, password)
    status = "SUCCESS" if result else "FAILED"
    print(f"  [{correo} / {password}] => {status} (active={user['activo']}, role={user['rol']})")

print("\nDone!")
