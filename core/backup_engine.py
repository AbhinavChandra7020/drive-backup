from auth import authenticate_google_drive
import os
from pathlib import Path

class BackupEngine:
    def __init__(self):
        self.drive = None
        
    def authenticate(self):
        """Authenticate with Google Drive"""
        try:
            self.drive = authenticate_google_drive()
            return True
        except Exception as e:
            raise Exception(f"Authentication failed: {str(e)}")
    
    def create_folder_in_drive(self, folder_name, parent_id='root'):
        """Create a folder in Google Drive"""
        folder_metadata = {
            'title': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [{'id': parent_id}]
        }
        
        folder = self.drive.CreateFile(folder_metadata)
        folder.Upload()
        return folder['id']
    
    def upload_file_to_drive(self, file_path, drive_folder_id, progress_callback=None):
        """Upload a single file to Google Drive"""
        try:
            file_metadata = {
                'title': os.path.basename(file_path),
                'parents': [{'id': drive_folder_id}]
            }
            
            drive_file = self.drive.CreateFile(file_metadata)
            drive_file.SetContentFile(file_path)
            drive_file.Upload()
            
            return True, None
        except Exception as e:
            return False, str(e)
    
    def start_backup(self, folder_path, files_info, progress_callback=None):
        """Start the backup process"""
        try:
            # Step 1: Authenticate
            if progress_callback:
                progress_callback(0.1, "🔐 Authenticating with Google Drive...")
            
            self.authenticate()
            
            # Step 2: Create main backup folder
            if progress_callback:
                progress_callback(0.2, "📁 Creating backup folder...")
            
            backup_folder_name = f"Backup_{Path(folder_path).name}"
            main_folder_id = self.create_folder_in_drive(backup_folder_name)
            
            # We'll add file upload logic here next
            
            return True, "Backup setup complete!"
            
        except Exception as e:
            return False, f"Backup failed: {str(e)}"