import os
import json
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path

# Try to import optional libraries
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

# Configuration
ROOT_DIR = Path(__file__).parent.resolve()
OUTPUT_FILE = ROOT_DIR / 'visited_files.json'

def load_json_data():
    """Load and parse the visited_files.json data"""
    try:
        if os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading JSON data: {e}")
        return []

def display_json_data(tree_view):
    """Display JSON data in the treeview widget"""
    # Clear existing data
    for item in tree_view.get_children():
        tree_view.delete(item)
    
    # Load data
    data = load_json_data()
    
    # Insert data into treeview
    for i, item in enumerate(data):
        # Format file size
        size_str = f"{item['size_kb']:.2f} KB"
        if item['size_kb'] > 1024:
            size_str = f"{item['size_kb']/1024:.2f} MB"
        
        # Insert into treeview
        tree_view.insert("", "end", text=str(i+1), values=(
            item['file_name'],
            item['extension'],
            size_str,
            item['last_modified'],
            item['file_path']
        ))

def search_files(tree_view, search_var, search_by_var):
    """Search through the files based on user input"""
    search_text = search_var.get().lower()
    search_field = search_by_var.get()
    
    # Clear existing data
    for item in tree_view.get_children():
        tree_view.delete(item)
    
    if not search_text:
        display_json_data(tree_view)
        return
    
    # Load data
    data = load_json_data()
    
    # Map search field option to actual field name
    field_map = {
        "File Name": "file_name",
        "Extension": "extension",
        "File Path": "file_path",
        "Last Modified": "last_modified"
    }
    
    field = field_map.get(search_field, "file_name")
    
    # Filter data
    filtered_data = []
    for item in data:
        if search_text in str(item[field]).lower():
            filtered_data.append(item)
    
    # Insert filtered data
    for i, item in enumerate(filtered_data):
        # Format file size
        size_str = f"{item['size_kb']:.2f} KB"
        if item['size_kb'] > 1024:
            size_str = f"{item['size_kb']/1024:.2f} MB"
        
        # Insert into treeview
        tree_view.insert("", "end", text=str(i+1), values=(
            item['file_name'],
            item['extension'],
            size_str,
            item['last_modified'],
            item['file_path']
        ))

def filter_by_extension(tree_view, extension_var):
    """Filter files by the selected extension type"""
    selected_ext = extension_var.get()
    
    # Clear existing data
    for item in tree_view.get_children():
        tree_view.delete(item)
    
    # Load data
    data = load_json_data()
    
    # Filter data if not showing all
    if selected_ext != "All Types":
        filtered_data = [item for item in data if item['extension'] == selected_ext]
    else:
        filtered_data = data
    
    # Insert filtered data
    for i, item in enumerate(filtered_data):
        # Format file size
        size_str = f"{item['size_kb']:.2f} KB"
        if item['size_kb'] > 1024:
            size_str = f"{item['size_kb']/1024:.2f} MB"
        
        # Insert into treeview
        tree_view.insert("", "end", text=str(i+1), values=(
            item['file_name'],
            item['extension'],
            size_str,
            item['last_modified'],
            item['file_path']
        ))

def show_file_details(tree_view):
    """Show details for the selected file in a popup window"""
    selected_item = tree_view.selection()
    if not selected_item:
        messagebox.showinfo("Information", "Please select a file to view details.")
        return
    
    # Get selected item details
    item_values = tree_view.item(selected_item[0], "values")
    if not item_values:
        return
    
    # Get style colors
    DARK_BG = "#282a36"
    LIGHT_BG = "#44475a"
    TEXT_COLOR = "#f8f8f2"
    
    # Create popup window
    details_window = tk.Toplevel()
    details_window.title("File Details")
    details_window.geometry("500x400")
    details_window.configure(bg=DARK_BG)
    details_window.grab_set()  # Make window modal
    
    # Add padding
    main_frame = ttk.Frame(details_window, padding=15)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # File name header
    ttk.Label(
        main_frame, 
        text=item_values[0],
        font=("Segoe UI", 14, "bold")
    ).pack(fill=tk.X, pady=(0, 15))
    
    # Details in a grid
    details_frame = ttk.Frame(main_frame)
    details_frame.pack(fill=tk.BOTH, pady=10)
    
    # Add detail rows
    fields = [
        ("File Name:", item_values[0]),
        ("Extension:", item_values[1]),
        ("Size:", item_values[2]),
        ("Last Modified:", item_values[3]),
        ("File Path:", item_values[4])
    ]
    
    for i, (label, value) in enumerate(fields):
        ttk.Label(
            details_frame, 
            text=label,
            font=("Segoe UI", 12, "bold")
        ).grid(row=i, column=0, sticky="w", padx=5, pady=5)
        
        # For file path, make it selectable
        if label == "File Path:":
            path_entry = ttk.Entry(details_frame, width=50)
            path_entry.insert(0, value)
            path_entry.configure(state="readonly")
            path_entry.grid(row=i, column=1, sticky="w", padx=5, pady=5)
        else:
            ttk.Label(
                details_frame, 
                text=value,
                font=("Segoe UI", 10)
            ).grid(row=i, column=1, sticky="w", padx=5, pady=5)
    
    # Open file button
    open_button = ttk.Button(
        main_frame, 
        text="Open File",
        command=lambda: open_file(item_values[4])
    )
    open_button.pack(side=tk.LEFT, pady=15, padx=5)
    
    # Close button
    ttk.Button(
        main_frame, 
        text="Close",
        command=details_window.destroy
    ).pack(side=tk.RIGHT, pady=15, padx=5)

def open_file(file_path):
    """Open a file with the default system application"""
    try:
        import subprocess
        import os
        import platform
        
        if platform.system() == 'Windows':
            os.startfile(file_path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.call(('open', file_path))
        else:  # Linux
            subprocess.call(('xdg-open', file_path))
            
        # Log a success message
        print(f"Opening file: {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open file: {str(e)}")
        print(f"Error opening file: {e}")

def export_data_to_csv(tree_view):
    """Export the current filtered view to a CSV file"""
    if not HAS_PANDAS:
        messagebox.showinfo("Information", "This feature requires pandas. Please install pandas to use this feature.")
        return
        
    items = tree_view.get_children()
    if not items:
        messagebox.showinfo("Information", "No data to export.")
        return
    
    # Get data from treeview
    data = []
    for item in items:
        values = tree_view.item(item, "values")
        data.append({
            "File Name": values[0],
            "Extension": values[1],
            "Size": values[2],
            "Last Modified": values[3],
            "File Path": values[4]
        })
    
    try:
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Export to CSV
        export_path = "visited_files_export.csv"
        df.to_csv(export_path, index=False)
        messagebox.showinfo("Success", f"Data exported successfully to {export_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export data: {str(e)}")

def get_file_stats():
    """Calculate statistics for the visited files"""
    data = load_json_data()
    
    if not data:
        return {
            "total_files": 0,
            "total_size": "0 KB",
            "by_extension": {},
            "largest_file": "None",
            "newest_file": "None"
        }
    
    # Calculate statistics
    total_files = len(data)
    total_size_kb = sum(item["size_kb"] for item in data)
    
    # Format total size
    if total_size_kb > 1024:
        total_size = f"{total_size_kb/1024:.2f} MB"
    else:
        total_size = f"{total_size_kb:.2f} KB"
    
    # Count by extension
    by_extension = {}
    for item in data:
        ext = item["extension"]
        if ext in by_extension:
            by_extension[ext] += 1
        else:
            by_extension[ext] = 1
    
    # Find largest file
    largest_file = max(data, key=lambda x: x["size_kb"])
    
    # Find newest file (based on modification time)
    try:
        newest_file = max(data, key=lambda x: time.strptime(x["last_modified"]))
    except:
        newest_file = data[-1]  # Just use the last one if parsing fails
    
    return {
        "total_files": total_files,
        "total_size": total_size,
        "by_extension": by_extension,
        "largest_file": largest_file["file_name"],
        "newest_file": newest_file["file_name"]
    }

def on_file_double_click(event, tree_view):
    """Handle double-click on a file in the treeview - open the file directly"""
    selected_item = tree_view.selection()
    if not selected_item:
        return
    
    # Get selected item details
    item_values = tree_view.item(selected_item[0], "values")
    if not item_values:
        return
    
    # Get the file path (5th column)
    file_path = item_values[4]
    
    # Open the file
    open_file(file_path)

def create_files_tab(parent):
    """Create the Visited Files Viewer tab"""
    # Create the main frame for the tab
    files_tab = ttk.Frame(parent)
    
    # Get style colors
    DARK_BG = "#282a36"
    LIGHT_BG = "#44475a"
    TEXT_COLOR = "#f8f8f2"
    ACCENT_COLOR = "#bd93f9"
    
    # Header with title and refresh button
    files_header = ttk.Frame(files_tab)
    files_header.pack(fill=tk.X, pady=(10, 15), padx=10)
    
    ttk.Label(
        files_header,
        text="Visited Files Explorer",
        font=("Segoe UI", 16, "bold")
    ).pack(side=tk.LEFT)
    
    # Statistics section
    stats_frame = ttk.LabelFrame(files_tab, text="File Statistics")
    stats_frame.pack(fill=tk.X, pady=(0, 15), padx=10)
    
    def update_stats_display(frame):
        # Clear existing widgets
        for widget in frame.winfo_children():
            widget.destroy()
        
        # Get statistics
        stats = get_file_stats()
        
        # Create grid layout for stats
        stats_grid = ttk.Frame(frame)
        stats_grid.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        # Total files and size
        totals_frame = ttk.Frame(stats_grid)
        totals_frame.pack(side=tk.LEFT, padx=20, pady=5)
        
        ttk.Label(
            totals_frame, 
            text="Total Files:",
            font=("Segoe UI", 11, "bold")
        ).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        ttk.Label(
            totals_frame,
            text=str(stats["total_files"]),
            font=("Segoe UI", 10)
        ).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(
            totals_frame,
            text="Total Size:",
            font=("Segoe UI", 11, "bold")
        ).grid(row=1, column=0, sticky="w", padx=5, pady=2)
        
        ttk.Label(
            totals_frame,
            text=stats["total_size"],
            font=("Segoe UI", 10)
        ).grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        # File highlights
        highlights_frame = ttk.Frame(stats_grid)
        highlights_frame.pack(side=tk.LEFT, padx=20, pady=5)
        
        ttk.Label(
            highlights_frame,
            text="Largest File:",
            font=("Segoe UI", 11, "bold")
        ).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        ttk.Label(
            highlights_frame,
            text=stats["largest_file"],
            font=("Segoe UI", 10)
        ).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(
            highlights_frame,
            text="Newest File:",
            font=("Segoe UI", 11, "bold")
        ).grid(row=1, column=0, sticky="w", padx=5, pady=2)
        
        ttk.Label(
            highlights_frame,
            text=stats["newest_file"],
            font=("Segoe UI", 10)
        ).grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        # Extension breakdown
        ext_frame = ttk.Frame(stats_grid)
        ext_frame.pack(side=tk.LEFT, padx=20, pady=5)
        
        ttk.Label(
            ext_frame,
            text="File Types:",
            font=("Segoe UI", 11, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        
        # Format extension counts
        row = 1
        for ext, count in sorted(stats["by_extension"].items(), key=lambda x: x[1], reverse=True)[:5]:  # Top 5 extensions
            ttk.Label(
                ext_frame,
                text=ext,
                font=("Segoe UI", 10)
            ).grid(row=row, column=0, sticky="w", padx=5, pady=1)
            
            ttk.Label(
                ext_frame,
                text=str(count),
                font=("Segoe UI", 10)
            ).grid(row=row, column=1, sticky="w", padx=5, pady=1)
            
            row += 1
    
    # Control panel for search and filter
    control_panel = ttk.Frame(files_tab)
    control_panel.pack(fill=tk.X, pady=(0, 10), padx=10)
    
    # Search controls
    search_frame = ttk.LabelFrame(control_panel, text="Search")
    search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    
    search_var = tk.StringVar()
    search_entry = ttk.Entry(
        search_frame,
        textvariable=search_var,
        font=("Segoe UI", 10)
    )
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
    
    # Search field dropdown
    search_by_var = tk.StringVar(value="File Name")
    search_by = ttk.Combobox(
        search_frame,
        textvariable=search_by_var,
        values=["File Name", "Extension", "File Path", "Last Modified"],
        state="readonly",
        width=15
    )
    search_by.pack(side=tk.LEFT, padx=5, pady=5)
    
    # Filter controls
    filter_frame = ttk.LabelFrame(control_panel, text="Filter")
    filter_frame.pack(side=tk.RIGHT, padx=(5, 0))
    
    ttk.Label(
        filter_frame,
        text="Extension:"
    ).pack(side=tk.LEFT, padx=5, pady=5)
    
    # Populate extensions from the data
    extensions = ["All Types"]
    try:
        data = load_json_data()
        unique_extensions = set(item["extension"] for item in data)
        extensions.extend(sorted(unique_extensions))
    except:
        pass
    
    extension_var = tk.StringVar(value="All Types")
    extension_combo = ttk.Combobox(
        filter_frame,
        textvariable=extension_var,
        values=extensions,
        state="readonly",
        width=15
    )
    extension_combo.pack(side=tk.LEFT, padx=5, pady=5)
    
    # Create the treeview first so we can reference it
    treeview_frame = ttk.Frame(files_tab)
    treeview_frame.pack(fill=tk.BOTH, expand=True, padx=10)
    
    # Create scrolled treeview
    tree_scroll = ttk.Scrollbar(treeview_frame)
    tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    files_tree = ttk.Treeview(
        treeview_frame,
        columns=("file_name", "extension", "size", "modified", "path"),
        show="headings",
        selectmode="browse",
        yscrollcommand=tree_scroll.set
    )
    tree_scroll.config(command=files_tree.yview)
    
    # Configure columns
    files_tree.heading("file_name", text="File Name")
    files_tree.heading("extension", text="Type")
    files_tree.heading("size", text="Size")
    files_tree.heading("modified", text="Last Modified")
    files_tree.heading("path", text="File Path")
    
    files_tree.column("file_name", width=250, minwidth=150)
    files_tree.column("extension", width=80, minwidth=80, anchor=tk.CENTER)
    files_tree.column("size", width=100, minwidth=80, anchor=tk.E)
    files_tree.column("modified", width=180, minwidth=150)
    files_tree.column("path", width=350, minwidth=200)
    
    files_tree.pack(fill=tk.BOTH, expand=True)
    
    # Now create buttons that reference the tree
    search_btn = ttk.Button(
        search_frame,
        text="Search",
        command=lambda: search_files(files_tree, search_var, search_by_var)
    )
    search_btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    filter_btn = ttk.Button(
        filter_frame,
        text="Apply Filter",
        command=lambda: filter_by_extension(files_tree, extension_var)
    )
    filter_btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    # Refresh button
    refresh_btn = ttk.Button(
        files_header,
        text="↻ Refresh",
        style="Accent.TButton",
        command=lambda: [display_json_data(files_tree), update_stats_display(stats_frame)]
    )
    refresh_btn.pack(side=tk.RIGHT)
    
    # Double-click to view details
    files_tree.bind("<Double-1>", lambda e: on_file_double_click(e, files_tree))
    
    # Action buttons
    action_frame = ttk.Frame(files_tab)
    action_frame.pack(fill=tk.X, pady=(10, 0), padx=10)
    
    # Export button (only if pandas is available)
    if HAS_PANDAS:
        export_btn = ttk.Button(
            action_frame,
            text="Export to CSV",
            command=lambda: export_data_to_csv(files_tree)
        )
        export_btn.pack(side=tk.RIGHT, padx=5)
    
    details_btn = ttk.Button(
        action_frame,
        text="View Details",
        command=lambda: show_file_details(files_tree)
    )
    details_btn.pack(side=tk.RIGHT, padx=5)
    
    # Load initial data and update stats
    display_json_data(files_tree)
    update_stats_display(stats_frame)
    
    return files_tab