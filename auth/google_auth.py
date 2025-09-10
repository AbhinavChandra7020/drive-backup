from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def authenticate_google_drive():
    
    # connecting to google
    gauth = GoogleAuth("settings.yaml")
    gauth.LoadCredentialsFile("token.json")
    
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    
    # Save credentials for next time
    gauth.SaveCredentialsFile("token.json")
    
    return GoogleDrive(gauth)