from auth import authenticate_google_drive
import os
from pathlib import Path

class BackupEngine:
    def __init__(self):
        self.drive = None
        self.folder_cache = {}  # Cache created folders to avoid duplicates
        
    def authenticate(self):
        """Authenticate with Google Drive"""
        try:
            self.drive = authenticate_google_drive()
            return True
        except Exception as e:
            raise Exception(f"Authentication failed: {str(e)}")
    
    def create_folder_in_drive(self, folder_name, parent_id='root'):
        """Create a folder in Google Drive"""
        # Check if we already created this folder
        cache_key = f"{parent_id}/{folder_name}"
        if cache_key in self.folder_cache:
            return self.folder_cache[cache_key]
            
        folder_metadata = {
            'title': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [{'id': parent_id}]
        }
        
        folder = self.drive.CreateFile(folder_metadata)
        folder.Upload()
        
        # Cache the folder ID
        self.folder_cache[cache_key] = folder['id']
        return folder['id']
    
    def create_folder_structure(self, folders_found, main_folder_id, progress_callback=None):
        """Create all necessary folders in Google Drive"""
        folder_ids = {'': main_folder_id}  # Empty string = root of backup
        
        # Sort folders to create parent folders first
        sorted_folders = sorted(folders_found, key=lambda x: x.count('/'))
        
        for i, folder_path in enumerate(sorted_folders):
            if progress_callback:
                progress = 0.3 + (i / len(sorted_folders)) * 0.2  # 30-50% progress
                progress_callback(progress, f"📁 Creating folder: {folder_path}")
            
            # Find parent folder
            parent_path = str(Path(folder_path).parent) if Path(folder_path).parent != Path('.') else ''
            parent_id = folder_ids.get(parent_path, main_folder_id)
            
            # Create folder
            folder_name = Path(folder_path).name
            folder_id = self.create_folder_in_drive(folder_name, parent_id)
            folder_ids[folder_path] = folder_id
        
        return folder_ids
    
    def upload_file_to_drive(self, file_path, drive_folder_id):
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
    
    def start_backup(self, folder_path, scan_results, progress_callback=None):
        """Start the backup process"""
        try:
            # Step 1: Authenticate
            if progress_callback:
                progress_callback(0.05, "🔐 Authenticating with Google Drive...")
            
            self.authenticate()
            
            # Step 2: Create main backup folder
            if progress_callback:
                progress_callback(0.1, "📁 Creating main backup folder...")
            
            backup_folder_name = f"Backup_{Path(folder_path).name}"
            main_folder_id = self.create_folder_in_drive(backup_folder_name)
            
            # Step 3: Create folder structure
            if progress_callback:
                progress_callback(0.2, "📁 Creating folder structure...")
            
            folder_ids = self.create_folder_structure(
                scan_results['folders_found'], 
                main_folder_id, 
                progress_callback
            )
            
            # Step 4: Get all files to upload
            if progress_callback:
                progress_callback(0.5, "📂 Preparing file list...")
            
            # Re-scan to get individual files with their folder info
            from core.file_scanner import FileScanner
            scanner = FileScanner(folder_path)
            files_to_upload = []
            
            root_path = Path(folder_path)
            for file_path in root_path.rglob('*'):
                if file_path.is_file():
                    try:
                        relative_path = file_path.relative_to(root_path)
                        folder_path_str = str(relative_path.parent) if relative_path.parent != Path('.') else ''
                        
                        files_to_upload.append({
                            'file_path': str(file_path),
                            'folder_path': folder_path_str,
                            'filename': file_path.name
                        })
                    except (PermissionError, OSError):
                        continue
            
            # Step 5: Upload files
            total_files = len(files_to_upload)
            uploaded_count = 0
            failed_count = 0
            
            for i, file_info in enumerate(files_to_upload):
                # Calculate progress (50-95% for file uploads)
                progress = 0.5 + (i / total_files) * 0.45
                if progress_callback:
                    progress_callback(progress, f"⬆️ Uploading: {file_info['filename']} ({i+1}/{total_files})")
                
                # Get the correct folder ID
                target_folder_id = folder_ids.get(file_info['folder_path'], main_folder_id)
                
                # Upload file
                success, error = self.upload_file_to_drive(file_info['file_path'], target_folder_id)
                
                if success:
                    uploaded_count += 1
                else:
                    failed_count += 1
                    print(f"Failed to upload {file_info['filename']}: {error}")
            
            # Final step
            if progress_callback:
                progress_callback(1.0, "✅ Backup complete!")
            
            result_message = f"Backup complete! {uploaded_count} files uploaded successfully"
            if failed_count > 0:
                result_message += f", {failed_count} files failed"
            
            return True, result_message
            
        except Exception as e:
            return False, f"Backup failed: {str(e)}"