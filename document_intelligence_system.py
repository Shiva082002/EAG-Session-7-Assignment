import os
import sys
import time
import json
import threading
import queue
import tkinter as tk
from tkinter import ttk, scrolledtext, font, messagebox
import subprocess
from datetime import datetime
from pathlib import Path

# Try to import optional libraries
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    import faiss
    import numpy as np
    from markitdown import MarkItDown
    from tqdm import tqdm
    import requests
    HAS_PROCESSING = True
except ImportError:
    HAS_PROCESSING = False

# Configuration
ROOT_DIR = Path(__file__).parent.resolve()
OUTPUT_FILE = ROOT_DIR / 'visited_files.json'
SUPPORTED_EXTENSIONS = {'.pdf', '.xlsx', '.xls', '.docx', '.doc', '.md', '.txt', '.pptx', '.ppt', '.csv', '.json', '.html', '.xml', '.md'}

# Colors and styles - using a modern dark theme
DARK_BG = "#2E3440"  # Dark background
LIGHT_BG = "#ECEFF4"  # Lighter background for contrast
TEXT_COLOR = "#ECEFF4"  # White text color
ACCENT_COLOR = "#878c94"  # Red accent
SUCCESS_COLOR = "#50fa7b"  # Green success
WARNING_COLOR = "#f1fa8c"  # Yellow warning
ERROR_COLOR = "#ff5555"  # Red error
INFO_COLOR = "#8be9fd"  # Cyan info

# Button style colors
BUTTON_BG = "#2f3441"  # Black background for buttons
BUTTON_FG = "#ffffff"  # White text for buttons
BUTTON_BORDER = "#2f3441"  # Red outline for buttons

# Import tab modules
from agent_tab import create_agent_tab
from files_tab import create_files_tab
from monitor_tab import create_monitor_tab

def create_ui():
    """Create the main application UI"""
    root = tk.Tk()
    root.title("Document Intelligence System")
    root.geometry("800x700")
    root.minsize(900, 600)
    
    # Configure root background
    root.configure(bg=DARK_BG)
    
    # Set fonts for the application
    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(family="Segoe UI", size=10)
    
    # Configure styles
    style = ttk.Style(root)
    style.theme_use('classic')  # Use clam theme as base
    
    style.configure('TNotebook.Tab', background='#cccccc')  # Inactive tab color
    style.map('TNotebook.Tab', background=[('selected', '#878c94')])  # Active tab color
    
    # Configure common elements
    style.configure("TFrame", background=DARK_BG)
    style.configure("TLabel", background=DARK_BG, foreground=TEXT_COLOR)
    style.configure("TLabelframe", background=DARK_BG, foreground=TEXT_COLOR)
    style.configure("TLabelframe.Label", background=DARK_BG, foreground=TEXT_COLOR)
    style.configure("TNotebook", background=DARK_BG, tabmargins=[2, 5, 2, 0])
    style.configure("TNotebook.Tab", background=DARK_BG, foreground=TEXT_COLOR, padding=[10, 2])
    
    # Configure button styles with black background, red outlines and white text
    style.configure("TButton", 
                   background=BUTTON_BG, 
                   foreground=BUTTON_FG, 
                   bordercolor=BUTTON_BORDER,
                   borderwidth=2,
                   focusthickness=3, 
                   focuscolor=ACCENT_COLOR)
    
    style.map("TButton",
             background=[("active", ACCENT_COLOR)],
             foreground=[("active", "white")])
    
    style.configure("Secondary.TButton", 
                   background="#3B4252", 
                   foreground=TEXT_COLOR)
    
    style.map("Secondary.TButton",
             background=[("active", "#4C566A")],
             foreground=[("active", "white")])
    
    # Create notebook for tabs
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create and add the Agent tab
    agent_tab, agent_callbacks = create_agent_tab(notebook)
    notebook.add(agent_tab, text="Agent Interface")
    
    # Create and add the Files tab
    files_tab = create_files_tab(notebook)
    notebook.add(files_tab, text="Visited Files Viewer")
    
    # Create and add the Monitor tab
    monitor_tab, monitor_callbacks = create_monitor_tab(notebook)
    notebook.add(monitor_tab, text="File Monitor & Processor")
    
    # Set up cleanup on window close
    def on_closing():
        # Clean up agent if running
        if agent_callbacks['is_running']():
            agent_callbacks['stop']()
        
        # Clean up monitor if running
        if monitor_callbacks['is_monitor_running']():
            monitor_callbacks['stop_monitoring']()
        
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    return root

# ============== Main Entry Point ==============

if __name__ == "__main__":
    # Run the application
    root = create_ui()
    root.mainloop()