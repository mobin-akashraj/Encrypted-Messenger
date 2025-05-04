import socket
import threading
import json
import customtkinter as ctk
from cryptography.fernet import Fernet
from datetime import datetime
from PIL import Image, ImageTk
import os
from typing import Optional
import time

# Init
ctk.set_appearance_mode("system")  # Use system theme by default, with toggle option
ctk.set_default_color_theme("blue")

# Constants
THEME_COLORS = {
    "dark": {
        "bg_primary": "#121212",
        "bg_secondary": "#1e1e1e",
        "accent": "#3e8ef7",
        "accent_hover": "#2b6cb0",
        "text_primary": "#f0f0f0",
        "text_secondary": "#a0a0a0",
        "user_bubble": "#3e8ef7",
        "other_bubble": "#2d2d2d",
        "input_bg": "#2d2d2d"
    },
    "light": {
        "bg_primary": "#f5f5f5",
        "bg_secondary": "#ffffff",
        "accent": "#3e8ef7",
        "accent_hover": "#2b6cb0",
        "text_primary": "#202020",
        "text_secondary": "#606060",
        "user_bubble": "#3e8ef7",
        "other_bubble": "#e6e6e6",
        "input_bg": "#ffffff"
    }
}

class MessageApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Secure Messenger")
        self.geometry("600x750")
        self.minsize(500, 600)
        
        # App state
        self.theme = "dark"  # Fixed dark theme
        self.username = ""
        self.users_online = []
        self.client = None
        self.cipher = None
        self.status = "disconnected"
        
        # Create login screen first
        self.create_login_screen()
        
    def create_login_screen(self):
        # Clear any existing widgets
        for widget in self.winfo_children():
            widget.destroy()
            
        # Create login frame
        login_frame = ctk.CTkFrame(self, corner_radius=20)
        login_frame.pack(pady=100, padx=40, fill="both", expand=False)
        
        # App title
        title_label = ctk.CTkLabel(login_frame, text="Secure Messenger", 
                                font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"))
        title_label.pack(pady=(20, 5))
        
        subtitle_label = ctk.CTkLabel(login_frame, text="End-to-End Encrypted Chat", 
                                    font=ctk.CTkFont(family="Segoe UI", size=14))
        subtitle_label.pack(pady=(0, 20))
        
        # Username input
        username_label = ctk.CTkLabel(login_frame, text="Username", 
                                    font=ctk.CTkFont(family="Segoe UI", size=14))
        username_label.pack(anchor="w", padx=25, pady=(15, 5))
        
        self.username_entry = ctk.CTkEntry(login_frame, placeholder_text="Enter username",
                                        font=ctk.CTkFont(family="Segoe UI", size=14),
                                        height=40, width=300, corner_radius=10)
        self.username_entry.pack(padx=25, pady=(0, 15))
        self.username_entry.focus()
        
        # Server address input
        server_label = ctk.CTkLabel(login_frame, text="Server Address", 
                                  font=ctk.CTkFont(family="Segoe UI", size=14))
        server_label.pack(anchor="w", padx=25, pady=(5, 5))
        
        self.server_entry = ctk.CTkEntry(login_frame, placeholder_text="192.168.1.2",
                                       font=ctk.CTkFont(family="Segoe UI", size=14),
                                       height=40, width=300, corner_radius=10)
        self.server_entry.pack(padx=25, pady=(0, 15))
        self.server_entry.insert(0, "192.168.1.2")
        
        # Port input
        port_label = ctk.CTkLabel(login_frame, text="Port", 
                                font=ctk.CTkFont(family="Segoe UI", size=14))
        port_label.pack(anchor="w", padx=25, pady=(5, 5))
        
        self.port_entry = ctk.CTkEntry(login_frame, placeholder_text="5555",
                                     font=ctk.CTkFont(family="Segoe UI", size=14),
                                     height=40, width=300, corner_radius=10)
        self.port_entry.pack(padx=25, pady=(0, 15))
        self.port_entry.insert(0, "5555")
        
        # Connect button
        connect_btn = ctk.CTkButton(login_frame, text="Connect", 
                                   font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                                   height=45, corner_radius=10, command=self.connect_to_server)
        connect_btn.pack(padx=25, pady=(15, 20), fill="x")
        
        # Version info
        version_label = ctk.CTkLabel(login_frame, text="v2.0", 
                                   font=ctk.CTkFont(family="Segoe UI", size=12),
                                   text_color=THEME_COLORS[self.theme]["text_secondary"])
        version_label.pack(pady=(0, 15))
        
        # Bind Enter key to connect
        self.username_entry.bind("<Return>", lambda e: self.connect_to_server())
        self.server_entry.bind("<Return>", lambda e: self.connect_to_server())
        self.port_entry.bind("<Return>", lambda e: self.connect_to_server())
    
    def connect_to_server(self):
        username = self.username_entry.get().strip()
        server = self.server_entry.get().strip()
        port = self.port_entry.get().strip()
        
        if not username:
            self.show_error("Please enter a username")
            return
            
        if not server:
            self.show_error("Please enter a server address")
            return
            
        if not port or not port.isdigit():
            self.show_error("Please enter a valid port number")
            return
            
        try:
            port = int(port)
            self.username = username
            
            # Initialize encryption
            aes_key = b'SXGguPKB6mbAFrfEKLE6uJko4Xu2DkLkPe2VJ8cAFeA='
            self.cipher = Fernet(aes_key)
            
            # Create socket and connect
            self.client = socket.socket()
            self.client.connect((server, port))
            self.client.send(json.dumps({"username": username}).encode())
            
            # If connection successful, switch to chat screen
            self.create_chat_interface()
            
            # Start listening for messages
            threading.Thread(target=self.receive_messages, daemon=True).start()
            
        except Exception as e:
            self.show_error(f"Connection failed: {str(e)}")
    
    def show_error(self, message):
        error_window = ctk.CTkToplevel(self)
        error_window.title("Error")
        error_window.geometry("400x200")
        error_window.resizable(False, False)
        
        # Center the window
        error_window.update_idletasks()
        x = (error_window.winfo_screenwidth() - error_window.winfo_width()) // 2
        y = (error_window.winfo_screenheight() - error_window.winfo_height()) // 2
        error_window.geometry(f"+{x}+{y}")
        
        # Error message
        error_label = ctk.CTkLabel(error_window, text=message,
                                 font=ctk.CTkFont(family="Segoe UI", size=16))
        error_label.pack(pady=(40, 20))
        
        # OK button
        ok_btn = ctk.CTkButton(error_window, text="OK", width=100, height=35,
                             command=error_window.destroy)
        ok_btn.pack(pady=(0, 20))
    
    def create_chat_interface(self):
        # Clear any existing widgets
        for widget in self.winfo_children():
            widget.destroy()
            
        # Update window title with username
        self.title(f"Secure Messenger - {self.username}")
        self.status = "connected"
        
        # Main content frame
        main_frame = ctk.CTkFrame(self, fg_color=THEME_COLORS[self.theme]["bg_primary"], corner_radius=0)
        main_frame.pack(fill="both", expand=True)
        
        # Header frame
        header_frame = ctk.CTkFrame(main_frame, fg_color=THEME_COLORS[self.theme]["bg_secondary"], 
                                   height=60, corner_radius=0)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)
        
        # App title in header
        title_label = ctk.CTkLabel(header_frame, text="Secure Messenger",
                                 font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"))
        title_label.pack(side="left", padx=(20, 0))
        
        # Status indicator
        self.status_frame = ctk.CTkFrame(header_frame, fg_color="#22c55e", width=12, height=12, corner_radius=6)
        self.status_frame.pack(side="left", padx=(10, 0))
        
        # Chat container - will hold messages and sidebar
        chat_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        chat_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Create chat area
        chat_area = ctk.CTkFrame(chat_container, fg_color=THEME_COLORS[self.theme]["bg_primary"], corner_radius=0)
        chat_area.pack(side="left", fill="both", expand=True)
        
        # Scrollable message area
        self.messages_frame = ctk.CTkScrollableFrame(chat_area, fg_color="transparent", 
                                                  corner_radius=0)
        self.messages_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Input area frame
        input_area = ctk.CTkFrame(chat_area, height=80, fg_color=THEME_COLORS[self.theme]["bg_secondary"],
                                corner_radius=20)
        input_area.pack(fill="x", side="bottom", padx=15, pady=15)
        input_area.pack_propagate(False)
        
        # Message input
        self.message_entry = ctk.CTkEntry(input_area, placeholder_text="Type your message...",
                                        font=ctk.CTkFont(family="Segoe UI", size=14),
                                        height=50, corner_radius=25, 
                                        fg_color=THEME_COLORS[self.theme]["input_bg"],
                                        border_width=0)
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(20, 10), pady=15)
        self.message_entry.bind("<Return>", lambda e: self.send_message())
        
        # Send button
        send_btn = ctk.CTkButton(input_area, text="➤", width=40, height=40, 
                               corner_radius=20, fg_color=THEME_COLORS[self.theme]["accent"],
                               hover_color=THEME_COLORS[self.theme]["accent_hover"],
                               command=self.send_message)
        send_btn.pack(side="right", padx=(0, 20), pady=15)
        
        # Welcome message
        self.add_system_message(f"Welcome to Secure Messenger, {self.username}!")
        self.add_system_message("Your messages are encrypted end-to-end.")
        
        # Focus the message entry
        self.message_entry.focus()
        
    def add_message_bubble(self, text, timestamp, is_user=False):
        """Adds a message bubble to the chat"""
        colors = THEME_COLORS[self.theme]
        
        # Create a frame for this message
        bubble_frame = ctk.CTkFrame(self.messages_frame, fg_color="transparent")
        bubble_frame.pack(fill="x", pady=5, padx=10, anchor="e" if is_user else "w")
        
        # Message frame - different colors for user vs others
        msg_bg = colors["user_bubble"] if is_user else colors["other_bubble"]
        text_color = "#ffffff" if is_user else colors["text_primary"]
        
        # Add username label if not user's message
        if not is_user:
            name_label = ctk.CTkLabel(bubble_frame, 
                                    text=text.split(":")[0] if ":" in text else "Unknown",
                                    font=ctk.CTkFont(family="Segoe UI", size=12),
                                    text_color=colors["text_secondary"])
            name_label.pack(anchor="w", padx=(10, 0), pady=(0, 2))
            
            # Extract the actual message if it contains a username
            if ":" in text:
                text = ":".join(text.split(":")[1:]).strip()
        
        # Message content
        message_container = ctk.CTkFrame(bubble_frame, fg_color=msg_bg, corner_radius=18)
        message_container.pack(side="right" if is_user else "left", anchor="e" if is_user else "w")
        
        # Message text
        message_text = ctk.CTkLabel(message_container, text=text, 
                                  font=ctk.CTkFont(family="Segoe UI", size=14),
                                  text_color=text_color, 
                                  wraplength=350, 
                                  justify="left")
        message_text.pack(padx=15, pady=10)
        
        # Timestamp
        time_label = ctk.CTkLabel(message_container, text=timestamp,
                                font=ctk.CTkFont(family="Segoe UI", size=10),
                                text_color="#d0d0d0" if is_user else colors["text_secondary"])
        time_label.pack(padx=10, pady=(0, 5), anchor="se")
        
        # Scroll to bottom
        self.messages_frame._parent_canvas.yview_moveto(1.0)
    
    def add_system_message(self, text):
        """Adds a system message to the chat"""
        colors = THEME_COLORS[self.theme]
        
        # Create a frame for this message
        system_frame = ctk.CTkFrame(self.messages_frame, fg_color="transparent")
        system_frame.pack(fill="x", pady=5)
        
        # System message container
        system_container = ctk.CTkFrame(system_frame, fg_color=colors["bg_secondary"], 
                                      corner_radius=10)
        system_container.pack(anchor="center")
        
        # System message text
        system_text = ctk.CTkLabel(system_container, text=text,
                                 font=ctk.CTkFont(family="Segoe UI", size=12),
                                 text_color=colors["text_secondary"])
        system_text.pack(padx=15, pady=5)
        
        # Scroll to bottom
        self.messages_frame._parent_canvas.yview_moveto(1.0)
    
    # Theme and emoji methods removed
    
    def send_message(self):
        """Sends a message to the server"""
        msg = self.message_entry.get().strip()
        if msg:
            try:
                enc_msg = self.cipher.encrypt(msg.encode()).decode()
                payload = {"from": self.username, "data": enc_msg}
                self.client.send(json.dumps(payload).encode())
                
                # Display in chat
                current_time = datetime.now().strftime("%H:%M")
                self.add_message_bubble(msg, current_time, is_user=True)
                
                # Clear input
                self.message_entry.delete(0, "end")
            except Exception as e:
                self.add_system_message(f"Error sending message: {str(e)}")
    
    def receive_messages(self):
        """Receives messages from the server in a separate thread"""
        while True:
            try:
                data = self.client.recv(4096)
                if not data:
                    break
                    
                msg = json.loads(data.decode())
                sender = msg["from"]
                dec_msg = self.cipher.decrypt(msg["data"].encode()).decode()
                
                # Format message with sender name if it's not a system message
                display_msg = f"{sender}: {dec_msg}" if sender != "SYSTEM" else dec_msg
                
                # Update UI in main thread
                current_time = datetime.now().strftime("%H:%M")
                self.after(0, lambda: self.add_message_bubble(display_msg, current_time, is_user=False))
                
            except Exception as e:
                self.after(0, lambda: self.add_system_message(f"Connection error: {str(e)}"))
                self.status = "disconnected"
                self.after(0, lambda: self.status_frame.configure(fg_color="#ef4444"))
                break

if __name__ == "__main__":
    app = MessageApp()
    app.mainloop()