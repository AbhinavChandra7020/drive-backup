import customtkinter as ctk

class ProgressWidget:
    def __init__(self, parent):
        self.parent = parent
        self.is_visible = False
        self.create_widgets()
    
    def create_widgets(self):
        """Create the progress bar widgets"""
        self.frame = ctk.CTkFrame(self.parent)
        
        self.label = ctk.CTkLabel(
            self.frame, 
            text="Ready...", 
            font=ctk.CTkFont(size=14)
        )
        self.label.pack(pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(self.frame)
        self.progress_bar.pack(pady=5, padx=20, fill="x")
        self.progress_bar.set(0)
        
        # Initially hidden
        self.hide()
    
    def show(self, after_widget=None):
        """Show the progress bar"""
        if after_widget:
            self.frame.pack(pady=10, padx=40, fill="x", after=after_widget)
        else:
            self.frame.pack(pady=10, padx=40, fill="x")
        self.is_visible = True
    
    def hide(self):
        """Hide the progress bar"""
        self.frame.pack_forget()
        self.is_visible = False
    
    def update(self, progress, message):
        """Update progress bar value and message
        
        Args:
            progress (float): Progress value between 0 and 1
            message (str): Status message to display
        """
        self.progress_bar.set(progress)
        self.label.configure(text=message)
    
    def reset(self):
        """Reset progress bar to initial state"""
        self.progress_bar.set(0)
        self.label.configure(text="Ready...")
    
    def set_indeterminate(self, message="Working..."):
        """Set progress bar to indeterminate mode with a message"""
        self.progress_bar.set(0.5)  # Middle position for indeterminate
        self.label.configure(text=message)
    
    def complete(self, message="Complete!"):
        """Set progress bar to complete state"""
        self.progress_bar.set(1.0)
        self.label.configure(text=message)