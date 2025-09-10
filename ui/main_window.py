import customtkinter as ctk
from tkinter import filedialog
import threading
from core.file_scanner import FileScanner
from core import BackupEngine
from ui.progress_widget import ProgressWidget

class MainWindow:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Drive Backup Tool")
        self.root.geometry("800x600")
        
        # Variables to store selections
        self.selected_folder = None
        self.scan_results = None  # Store scan results for backup
        
        ctk.set_appearance_mode("system")
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize all UI components"""
        self.create_header()
        self.create_folder_selection()
        self.create_progress_section()
        self.create_backup_button()
        self.create_results_section()
    
    def create_header(self):
        """Create the application header"""
        title = ctk.CTkLabel(
            self.root, 
            text="Drive Backup Tool", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=20)
    
    def create_folder_selection(self):
        """Create the folder selection section"""
        self.source_frame = ctk.CTkFrame(self.root)
        self.source_frame.pack(pady=20, padx=40, fill="x")
        
        ctk.CTkLabel(
            self.source_frame, 
            text="Select folder to backup:", 
            font=ctk.CTkFont(size=16)
        ).pack(pady=10)
        
        folder_button = ctk.CTkButton(
            self.source_frame, 
            text="Choose Folder", 
            command=self.select_folder
        )
        folder_button.pack(pady=10)
        
        self.folder_label = ctk.CTkLabel(self.source_frame, text="No folder selected")
        self.folder_label.pack(pady=5)
    
    def create_progress_section(self):
        """Create the progress bar section"""
        self.progress_widget = ProgressWidget(self.root)
    
    def create_backup_button(self):
        """Create the backup button"""
        self.backup_button = ctk.CTkButton(
            self.root,
            text="Start Scan",
            command=self.start_scan,
            font=ctk.CTkFont(size=16),
            height=40
        )
        self.backup_button.pack(pady=20)
    
    def create_results_section(self):
        """Create the results display section"""
        status_frame = ctk.CTkFrame(self.root)
        status_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        ctk.CTkLabel(
            status_frame, 
            text="Results:", 
            font=ctk.CTkFont(size=16)
        ).pack(anchor="w", padx=10, pady=(10,0))
        
        self.status_text = ctk.CTkTextbox(status_frame, height=200)
        self.status_text.pack(pady=10, padx=10, fill="both", expand=True)
        
    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder = folder
            self.folder_label.configure(text=f"Selected: {folder}")
            # Reset backup button when new folder selected
            self.backup_button.configure(text="Start Scan", command=self.start_scan)
    
    def show_results(self, folders_found, files_count, total_size):
        """Show scan results and enable backup"""
        # Store results for backup
        self.scan_results = {
            'folders_found': folders_found,
            'files_count': files_count,
            'total_size': total_size
        }
        
        # Hide progress bar
        self.progress_widget.hide()
        
        # Show results
        size_mb = total_size / (1024 * 1024)
        self.status_text.delete("1.0", "end")
        
        self.status_text.insert("end", f"✅ Scan Complete!\n")
        self.status_text.insert("end", f"Files found: {files_count}\n")
        self.status_text.insert("end", f"Total size: {size_mb:.2f} MB\n")
        self.status_text.insert("end", f"\nFolders found ({len(folders_found)}):\n")
        self.status_text.insert("end", "-" * 50 + "\n")
        
        for folder in sorted(folders_found):
            self.status_text.insert("end", f"📁 {folder}\n")
        
        # Change button to backup mode
        self.backup_button.configure(
            state="normal", 
            text="📤 Backup to Google Drive", 
            command=self.start_actual_backup
        )
    
    def scan_worker(self):
        """Worker thread for scanning"""
        
        scanner = FileScanner(self.selected_folder)
        
        def progress_callback(progress, message):
            self.root.after(0, self.progress_widget.update, progress, message)
        
        folders_found, files_count, total_size = scanner.scan_files(callback=progress_callback)
        self.root.after(0, self.show_results, folders_found, files_count, total_size)
    
    def backup_worker(self):
        """Worker thread for backup process"""
        
        backup_engine = BackupEngine()
        
        def progress_callback(progress, message):
            self.root.after(0, self.progress_widget.update, progress, message)
        
        try:
            success, message = backup_engine.start_backup(
                self.selected_folder, 
                self.scan_results,
                progress_callback
            )
            
            if success:
                self.root.after(0, self.show_backup_complete, message)
            else:
                self.root.after(0, self.show_backup_error, message)
                
        except Exception as e:
            self.root.after(0, self.show_backup_error, str(e))

    def show_backup_complete(self, message):
        """Show backup completion"""
        self.progress_widget.hide()
        self.status_text.insert("end", f"\n✅ {message}\n")
        self.backup_button.configure(state="normal", text="Start New Scan", command=self.reset_for_new_scan)

    def show_backup_error(self, error):
        """Show backup error"""
        self.progress_widget.hide()
        self.status_text.insert("end", f"\n❌ Backup Error: {error}\n")
        self.backup_button.configure(state="normal", text="📤 Retry Backup", command=self.start_actual_backup)

    def start_actual_backup(self):
        """Start the actual backup to Google Drive"""
        if not self.scan_results:
            self.status_text.insert("end", "❌ No scan results available. Please scan first.\n")
            return
            
        self.progress_widget.show(after_widget=self.backup_button)
        self.progress_widget.reset()
        self.backup_button.configure(state="disabled", text="Backing up...")
        
        # Start backup in background thread
        backup_thread = threading.Thread(target=self.backup_worker, daemon=True)
        backup_thread.start()

    def start_scan(self):
        """Start the folder scan"""
        if not self.selected_folder:
            self.status_text.delete("1.0", "end")
            self.status_text.insert("end", "❌ Please select a folder first!\n")
            return
        
        self.status_text.delete("1.0", "end")
        self.progress_widget.show(after_widget=self.source_frame)
        self.progress_widget.reset()
        
        self.backup_button.configure(state="disabled", text="Scanning...")
        
        scan_thread = threading.Thread(target=self.scan_worker, daemon=True)
        scan_thread.start()

    def reset_for_new_scan(self):
        """Reset UI for a new scan"""
        self.scan_results = None
        self.status_text.delete("1.0", "end")
        self.backup_button.configure(text="Start Scan", command=self.start_scan, state="normal")
        
    def run(self):
        self.root.mainloop()