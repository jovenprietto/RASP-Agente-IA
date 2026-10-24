import os
from google_auth_oauthlib.flow import InstalledAppFlow

# Permisos completos para leer y escribir en tu calendario
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    # Si estás por SSH en la misma red local, usamos la IP 0.0.0.0
    creds = flow.run_local_server(port=8088, open_browser=False)
    
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    print("[EXITO] token.json generado correctamente. El asistente ya tiene acceso.")

if __name__ == '__main__':
    main()
