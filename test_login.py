from web_panel.models.user import User

correo = 'anibalmonas124@gmail.com'
password = 'Admin123!'

print(f' Buscando usuario: {correo}')
user = User.get_by_email(correo)
if user:
    print(f' Usuario encontrado: {user.nombre} (rol: {user.rol})')
    print(f'Hash: {user.password_hash[:60]}...')
    if user.check_password(password):
        print('✅ Contraseña correcta')
    else:
        print(' Contraseña incorrecta')
else:
    print(' Usuario NO encontrado en la BD')
