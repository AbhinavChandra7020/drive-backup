from pathlib import Path
import os

class FileScanner:
    def __init__(self, root_folder):
        self.root_folder = Path(root_folder)

    def count_items(self, path):
        """Count total items for progress calculation"""
        total_items = 0
        try:
            for item in path.rglob('*'):
                total_items += 1
        except (PermissionError, OSError):
            pass
        return total_items

    def scan_files(self, callback=None):
        folders_found = set()
        files_count = 0
        total_size = 0
        processed_items = 0

        try:
            # First, count total items for progress tracking
            if callback:
                callback(0, "Counting items...")
            
            total_items = self.count_items(self.root_folder)
            
            if total_items == 0:
                if callback:
                    callback(1.0, "No items found")
                return folders_found, files_count, total_size

            # Now scan through all items
            for item_path in self.root_folder.rglob('*'):
                processed_items += 1
                progress = processed_items / total_items
                
                try:
                    if item_path.is_file():
                        files_count += 1
                        file_size = item_path.stat().st_size
                        total_size += file_size
                        
                        # Add the parent folder to our set
                        relative_parent = item_path.parent.relative_to(self.root_folder)
                        if str(relative_parent) != '.':  # Don't include root as a folder
                            folders_found.add(str(relative_parent))
                    
                    elif item_path.is_dir():
                        # Add directory to our set
                        relative_path = item_path.relative_to(self.root_folder)
                        if str(relative_path) != '.':  # Don't include root
                            folders_found.add(str(relative_path))
                    
                    # Update progress every 100 items or at the end
                    if processed_items % 100 == 0 or processed_items == total_items:
                        if callback:
                            callback(progress, f"Processed {processed_items}/{total_items} items...")

                except (PermissionError, OSError) as e:
                    if callback and processed_items % 100 == 0:
                        callback(progress, f"Processed {processed_items}/{total_items} items (some skipped)...")
                    continue

        except Exception as e:
            if callback:
                callback(1.0, f"Error during scan: {str(e)}")
        
        # Final progress update
        if callback:
            callback(1.0, "Scan complete!")
        
        return folders_found, files_count, total_size