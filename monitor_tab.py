import os
import sys
import time
import json
import threading
import queue
from pathlib import Path
import hashlib
import tkinter as tk
from tkinter import ttk, scrolledtext, font
from datetime import datetime

# Try to import optional dependencies
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False
    
try:
    import faiss
    import numpy as np
    from tqdm import tqdm
    import requests
    HAS_PROCESSING = True
except ImportError:
    HAS_PROCESSING = False

# Configuration
ROOT_DIR = Path(__file__).parent.resolve()
OUTPUT_FILE = ROOT_DIR / 'visited_files.json'
SUPPORTED_EXTENSIONS = {'.pdf', '.xlsx', '.xls', '.docx', '.doc', '.md', '.txt', '.pptx', '.ppt', '.csv'}
EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"
CHUNK_SIZE = 256
CHUNK_OVERLAP = 40

# Global flags and variables
monitor_running = False
processing_running = False
monitor_output_queue = queue.Queue()
process_output_queue = queue.Queue()
monitor_thread = None
processor_thread = None
observer = None
file_changes_detected = False
monitored_count = 0
processed_count = 0

# ============== File Monitoring Functions ==============

def load_visited_files():
    """Load previously visited files from JSON"""
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: {OUTPUT_FILE} is empty or corrupted. Resetting to an empty list.")
            return []
    return []

def save_to_json(data):
    """Save visited files to JSON"""
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

class FileAccessHandler(FileSystemEventHandler):
    def __init__(self, visited_files, visited_paths, ui_callback=None):
        self.visited_files = visited_files
        self.visited_paths = visited_paths
        self.ui_callback = ui_callback
        
    def on_any_event(self, event):
        print(event)
        if not event.is_directory and Path(event.src_path).suffix.lower() in SUPPORTED_EXTENSIONS:
            file_path = Path(event.src_path).resolve()
            # Skip temporary files
            if file_path.name.startswith('~$'):
                return
            # Skip already recorded files
            if str(file_path) in self.visited_paths:
                return
                
            try:
                # Add file information
                file_info = {
                    'file_name': file_path.name,
                    'file_path': str(file_path),
                    'extension': file_path.suffix,
                    'size_kb': round(file_path.stat().st_size / 1024, 2),
                    'last_modified': time.ctime(file_path.stat().st_mtime)
                }
                self.visited_files.append(file_info)
                self.visited_paths.add(str(file_path))
                
                # Save to JSON file
                save_to_json(self.visited_files)
                
                # Update global count
                global monitored_count, file_changes_detected
                monitored_count += 1
                file_changes_detected = True
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                log_monitor(f"[{timestamp}] ✓ Added to tracking: {file_path.name} ({file_info['size_kb']} KB)")
                
                # Update UI if callback provided
                if self.ui_callback:
                    self.ui_callback()
            except Exception as e:
                log_monitor(f"❌ Error processing file {file_path}: {str(e)}")
    
    # Also monitor created files, not just modified ones
    def on_created(self, event):
        self.on_modified(event)

def start_monitoring(path, ui_callback=None):
    """Start monitoring for file access"""
    global monitor_running, observer
    
    if monitor_running:
        log_monitor("File monitoring is already running.")
        return
    
    log_monitor(f"⏱️ Starting to monitor {path} for file access...")
    visited_files = load_visited_files()
    visited_paths = {file['file_path'] for file in visited_files}
    
    event_handler = FileAccessHandler(visited_files, visited_paths, ui_callback)
    observer = Observer()
    observer.schedule(event_handler, path=path, recursive=True)
    observer.start()
    monitor_running = True
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_monitor(f"[{timestamp}] 🟢 Monitoring active on {path}")
    log_monitor(f"Supported file types: {', '.join(SUPPORTED_EXTENSIONS)}")

def stop_monitoring():
    """Stop file monitoring"""
    global monitor_running, observer
    
    if not monitor_running or observer is None:
        log_monitor("File monitoring is not running.")
        return
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_monitor(f"[{timestamp}] ⏹️ Stopping file monitoring...")
    observer.stop()
    observer.join()
    monitor_running = False
    log_monitor(f"🛑 File monitoring stopped. Tracked {monitored_count} new files.")

# ============== Document Processing Functions ==============

class TqdmToLogger:
    """Custom tqdm output handler to capture progress bar output"""
    def __init__(self):
        self.output = ""
        
    def write(self, s):
        self.output = s.strip()
        log_process(s)
        
    def flush(self):
        pass

def get_embedding(text):
    """Get embeddings for text chunks"""
    response = requests.post(EMBED_URL, json={"model": EMBED_MODEL, "prompt": text})
    response.raise_for_status()
    return np.array(response.json()["embedding"], dtype=np.float32)

def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into chunks with overlap"""
    words = text.split()
    for i in range(0, len(words), size - overlap):
        yield " ".join(words[i:i+size])

def file_hash(path):
    """Calculate file hash to detect changes"""
    return hashlib.md5(Path(path).read_bytes()).hexdigest()

def process_documents():
    """Process documents and create FAISS index"""
    global processed_count, processing_running
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_process(f"[{timestamp}] 🔄 Starting document processing...")
    log_process(f"📊 Indexing documents...")
    
    try:
        # Set paths directly as in process.py
        ROOT_DIR = Path(__file__).parent.resolve()
        DOC_PATH = ROOT_DIR / "documents"
        INDEX_CACHE = ROOT_DIR / "faiss_index"
        INDEX_CACHE.mkdir(exist_ok=True)
        INDEX_FILE = INDEX_CACHE / "index.bin"
        METADATA_FILE = INDEX_CACHE / "metadata.json"
        CACHE_FILE = INDEX_CACHE / "doc_index_cache.json"
        VISITED_FILE = ROOT_DIR / "visited_files.json"

        # Check if we have the required packages for document conversion
        try:
            from markitdown import MarkItDown
            converter = MarkItDown()
        except ImportError:
            log_process("⚠️ MarkItDown package not found. Document processing will be limited.")
            processing_running = False  # Make sure to set this to False before returning
            return
        
        # Load data from files - simplified error handling
        CACHE_META = {}
        metadata = []
        index = None
        visited_data = []
        
        try:
            if CACHE_FILE.exists():
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    CACHE_META = json.load(f)
            
            if METADATA_FILE.exists():
                with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            
            if INDEX_FILE.exists():
                index = faiss.read_index(str(INDEX_FILE))
            
            if VISITED_FILE.exists():
                with open(VISITED_FILE, 'r', encoding='utf-8') as f:
                    visited_data = json.load(f)
        except Exception as e:
            log_process(f"⚠️ Error loading data files: {e}")
            # Continue with empty data structures rather than failing
        
        # Count files that need processing
        files_to_process = 0
        for entry in visited_data:
            file_path = Path(entry['file_path'])
            if not file_path.exists():
                continue
            try:
                fhash = file_hash(file_path)
                if entry['file_name'] in CACHE_META and CACHE_META[entry['file_name']] == fhash:
                    continue
                files_to_process += 1
            except Exception as e:
                log_process(f"⚠️ Error checking file hash for {file_path}: {e}")
        
        if files_to_process == 0:
            log_process("ℹ️ No new files to process.")
        else:
            log_process(f"📝 Found {files_to_process} file(s) to process")
        
        # Process each file from visited_files.json
        processed_file_count = 0
        for entry in visited_data:
            file_path = Path(entry['file_path'])
            if not file_path.exists():
                log_process(f"❌ File not found: {file_path}")
                continue

            try:
                fhash = file_hash(file_path)
                if entry['file_name'] in CACHE_META and CACHE_META[entry['file_name']] == fhash:
                    log_process(f"⏭️ Skipping unchanged file: {entry['file_name']}")
                    continue

                processed_file_count += 1
                processed_count += 1
                log_process(f"⚙️ Processing: {entry['file_name']} ({processed_file_count}/{files_to_process})")
                
                result = converter.convert(str(file_path))
                markdown = result.text_content
                chunks = list(chunk_text(markdown))
                embeddings_for_file = []
                new_metadata = []
                
                # Custom progress handler for tqdm
                tqdm_handler = TqdmToLogger()
                
                for i, chunk in enumerate(tqdm(chunks, desc=f"Embedding {entry['file_name']}", 
                                            file=tqdm_handler, position=0, leave=True)):
                    embedding = get_embedding(chunk)
                    embeddings_for_file.append(embedding)
                    new_metadata.append({
                        "doc": entry['file_name'],
                        "chunk": chunk,
                        "chunk_id": f"{file_path.stem}_{i}",
                        "file_path": str(file_path)
                    })
                    # Update the progress
                    progress_pct = round(((i+1) / len(chunks)) * 100)
                    log_process(f"▶️ Progress: {i+1}/{len(chunks)} chunks embedded ({progress_pct}%)", update_only=True)
                    
                if embeddings_for_file:
                    if index is None:
                        dim = len(embeddings_for_file[0])
                        index = faiss.IndexFlatL2(dim)
                    index.add(np.stack(embeddings_for_file))
                    metadata.extend(new_metadata)
                CACHE_META[entry['file_name']] = fhash
                timestamp = datetime.now().strftime("%H:%M:%S")
                log_process(f"[{timestamp}] ✅ Completed: {entry['file_name']} - {len(chunks)} chunks indexed")
            except Exception as e:
                log_process(f"❌ Failed to process {entry['file_name']}: {e}")

        # Save all data - directly write to files
        try:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(CACHE_META, f, indent=2)
                
            with open(METADATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
                
            if index and index.ntotal > 0:
                faiss.write_index(index, str(INDEX_FILE))
                timestamp = datetime.now().strftime("%H:%M:%S")
                log_process(f"[{timestamp}] 🎉 Processing complete: Saved FAISS index and metadata")
            else:
                log_process("⚠️ No new documents were processed.")
        except Exception as e:
            log_process(f"❌ Error saving data: {e}")
        
        # Reset the file changes flag
        global file_changes_detected
        file_changes_detected = False
        
    except Exception as e:
        log_process(f"❌ Critical processing error: {e}")
    finally:
        # Ensure processing_running is set to False regardless of success or failure
        log_process("💤 Document processing terminated")
        processing_running = False

# ============== UI and Threading Functions ==============

def log_monitor(message, update_only=False):
    """Log a message to the monitor output queue"""
    monitor_output_queue.put((message, update_only))

def log_process(message, update_only=False):
    """Log a message to the process output queue"""
    process_output_queue.put((message, update_only))

def update_output(text_widget, q, last_line_var=None):
    """Update text widget with content from queue"""
    try:
        got_line = False
        while True:
            try:
                message, update_only = q.get_nowait()
                if update_only and last_line_var is not None:
                    # Remove last progress line if exists
                    if last_line_var.get() != "":
                        text_widget.delete(f"end-1l linestart", "end-1l lineend")
                    # Add new progress line
                    text_widget.insert(tk.END, message + "\n")
                    last_line_var.set(message)
                else:
                    # Normal message, just append
                    text_widget.insert(tk.END, message + "\n")
                text_widget.see(tk.END)
                text_widget.update()  # Force immediate update
                got_line = True
            except queue.Empty:
                break
                
        # Schedule next update even if no lines were processed
        text_widget.after(10, lambda: update_output(text_widget, q, last_line_var))
    except Exception as e:
        print(f"Error updating output: {e}")
        text_widget.after(100, lambda: update_output(text_widget, q, last_line_var))

def monitor_worker(path, ui_callback=None):
    """Worker function for file monitoring thread"""
    try:
        start_monitoring(path, ui_callback)
        # Keep thread alive until monitoring is stopped
        while monitor_running:
            time.sleep(0.5)
    except Exception as e:
        log_monitor(f"❌ Error in monitoring thread: {str(e)}")

def process_worker():
    """Worker function for document processing thread"""
    global processing_running, processed_count
    
    try:
        processing_running = True
        # Set initial count to track progress
        initial_processed_count = processed_count
        
        # Run document processing
        process_documents()
        
        # Report how many new files were processed
        new_processed = processed_count - initial_processed_count
        log_process(f"🔢 Processing summary: {new_processed} new file(s) processed")
        
    except Exception as e:
        log_process(f"❌ Error in processing thread: {str(e)}")
    finally:
        # Ensure processing_running is set to False
        processing_running = False
        log_process(f"📋 Processing thread has terminated")
        
    return

def start_monitor_thread(monitor_output, progress_var, ui_callback=None):
    """Start file monitoring in a separate thread"""
    global monitor_thread, monitor_running, monitored_count
    
    if monitor_running or (monitor_thread is not None and monitor_thread.is_alive()):
        log_monitor("⚠️ File monitoring is already running.")
        return
    
    # Reset counter when starting new monitoring session
    monitored_count = 0
    
    # Monitor the entire D drive with the exact path format from test.py
    path = r'd:/'  # Using a raw string as in test.py
    
    log_monitor(f"⏱️ Starting to monitor {path} drive for file access...")
    
    if not os.path.exists(path):
        log_monitor(f"❌ Error: Drive {path} does not exist or is not accessible.")
        return
    
    progress_var.set(25)  # Update progress indicator
    monitor_thread = threading.Thread(target=monitor_worker, args=(path, ui_callback))
    monitor_thread.daemon = True
    monitor_thread.start()
    progress_var.set(100)  # Update progress indicator
    
    # Start updating output
    update_output(monitor_output, monitor_output_queue)

def stop_monitor_thread(progress_var):
    """Stop the file monitoring thread"""
    global monitor_running
    
    if not monitor_running:
        log_monitor("⚠️ File monitoring is not running.")
        return
    
    # Signal the monitoring thread to stop
    progress_var.set(25)  # Update progress indicator
    stop_monitoring()
    progress_var.set(100)  # Update progress indicator

def is_monitor_running():
    """Return the monitor running status"""
    global monitor_running
    return monitor_running

def is_processing_running():
    """Return the processing running status"""
    global processing_running
    return processing_running

def create_monitor_tab(parent):
    """Create the File Monitor tab"""
    # Check if required libraries are installed
    if not HAS_WATCHDOG:
        # Create a simple tab with installation instructions
        tab = ttk.Frame(parent)
        
        msg_frame = ttk.Frame(tab, padding=20)
        msg_frame.pack(expand=True, fill=tk.BOTH)
        
        ttk.Label(
            msg_frame, 
            text="Missing Required Libraries",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=(0, 20))
        
        ttk.Label(
            msg_frame,
            text="The File Monitor tab requires the watchdog library to function.",
            font=("Segoe UI", 12)
        ).pack(pady=(0, 10))
        
        cmd_frame = ttk.LabelFrame(msg_frame, text="Installation Command")
        cmd_frame.pack(pady=20, fill=tk.X)
        
        cmd_text = ttk.Entry(cmd_frame, font=("Consolas", 10))
        cmd_text.insert(0, "pip install watchdog")
        cmd_text.config(state="readonly")
        cmd_text.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Label(
            msg_frame,
            text="Please install the required library and restart the application.",
            font=("Segoe UI", 10)
        ).pack(pady=(20, 0))
        
        return tab, {}
    
    # Define custom styles for buttons and UI elements
    style = ttk.Style()
    
    # Colors and styles - using a more visible color scheme
    DARK_BG = "#2E3440"
    LIGHT_BG = "#ECEFF4"
    TEXT_COLOR = "#ECEFF4"
    BUTTON_BG = "#000000"  # Black background for buttons
    BUTTON_FG = "#ffffff"  # White text for buttons
    BUTTON_BORDER = "#ff0000"  # Red outline for buttons
    ACCENT_COLOR = "#ff0000"  # Red accent
    ACCENT_ALT = "#B48EAD"
    SUCCESS_COLOR = "#A3BE8C"
    WARNING_COLOR = "#EBCB8B"
    ERROR_COLOR = "#BF616A"
    INFO_COLOR = "#88C0D0"
    
    # Create custom styles if they don't exist
    if "Monitor.TButton" not in style.theme_names():
        style.configure(
            "Monitor.TButton",
            background=BUTTON_BG,
            foreground=BUTTON_FG,
            font=("Segoe UI", 10, "bold"),
            padding=6,
            bordercolor=BUTTON_BORDER,
            borderwidth=2
        )
        
        style.map(
            "Monitor.TButton",
            background=[("active", ACCENT_COLOR)],
            foreground=[("active", "white")]
        )
    
    # Create the main frame for the tab
    monitor_tab = ttk.Frame(parent)
    
    # Header with title and status
    header_frame = ttk.Frame(monitor_tab)
    header_frame.pack(fill=tk.X, pady=(10, 15))
    
    ttk.Label(
        header_frame,
        text="File Monitor & Processing System",
        font=("Segoe UI", 16, "bold")
    ).pack(side=tk.LEFT, padx=10)
    
    # Status indicators
    status_frame = ttk.Frame(header_frame)
    status_frame.pack(side=tk.RIGHT, padx=10)
    
    monitored_var = tk.StringVar(value="Files Detected: 0")
    monitored_label = ttk.Label(
        status_frame,
        textvariable=monitored_var,
        font=("Segoe UI", 10, "bold")
    )
    monitored_label.pack(side=tk.LEFT, padx=(0, 15))
    
    processed_var = tk.StringVar(value="Files Processed: 0")
    processed_label = ttk.Label(
        status_frame,
        textvariable=processed_var,
        font=("Segoe UI", 10, "bold")
    )
    processed_label.pack(side=tk.LEFT)
    
    # Status label with more visibility
    status_var = tk.StringVar(value="Status: Ready to monitor")
    status_label = ttk.Label(
        status_frame,
        textvariable=status_var,
        font=("Segoe UI", 10, "bold"),
        foreground="#5E81AC"
    )
    status_label.pack(side=tk.BOTTOM, pady=(5,0))
    
    # Control panel
    control_frame = ttk.LabelFrame(monitor_tab, text="Control Panel")
    control_frame.pack(fill=tk.X, pady=(0, 15), padx=10)
    
    # Progress bar with better visibility
    progress_var = tk.IntVar(value=0)
    progress = ttk.Progressbar(
        control_frame, 
        variable=progress_var,
        mode="determinate",
        length=200
    )
    progress.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
    
    # Variable to track the last progress line
    last_line_var = tk.StringVar(value="")
    
    # Buttons frame
    buttons_frame = ttk.Frame(control_frame, padding=10)
    buttons_frame.pack(fill=tk.X)

    # Single control button that toggles between Start/Stop and processes when stopped
    # Using a more visible button style
    control_btn = ttk.Button(
        buttons_frame,
        text="Start Monitoring",
        width=30,
        style="Monitor.TButton"
    )
    control_btn.pack(side=tk.LEFT, padx=10, pady=10)

    # Information label with improved visibility
    info_label = ttk.Label(
        control_frame,
        text="Click 'Start Monitoring' to begin tracking files. When you click 'Stop Monitoring', files will be processed automatically.",
        font=("Segoe UI", 10),
        foreground="#5E81AC",
        wraplength=550
    )
    info_label.pack(pady=(0, 10), padx=10)
    
    # Split pane for logs
    paned = ttk.PanedWindow(monitor_tab, orient=tk.HORIZONTAL)
    paned.pack(fill=tk.BOTH, expand=True, padx=10)
    
    # Monitor output area
    monitor_frame = ttk.LabelFrame(paned, text="File Monitor Log")
    paned.add(monitor_frame, weight=1)
    
    # Use a more readable font and better contrast
    monitor_output = scrolledtext.ScrolledText(
        monitor_frame, 
        wrap=tk.WORD,
        font=("Consolas", 10),
        bg=DARK_BG,
        fg=TEXT_COLOR,
        padx=5,
        pady=5
    )
    monitor_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Configure text tags for styling with better visibility
    monitor_output.tag_configure("header", foreground="#81A1C1", font=("Consolas", 11, "bold"))
    monitor_output.tag_configure("info", foreground="#88C0D0")
    monitor_output.tag_configure("error", foreground="#BF616A")
    monitor_output.tag_configure("system", foreground="#EBCB8B")
    monitor_output.tag_configure("success", foreground="#A3BE8C")
    
    # Process output area
    process_frame = ttk.LabelFrame(paned, text="Document Processing Log")
    paned.add(process_frame, weight=1)
    
    # Use a more readable font and better contrast
    process_output = scrolledtext.ScrolledText(
        process_frame, 
        wrap=tk.WORD,
        font=("Consolas", 10),
        bg=DARK_BG,
        fg=TEXT_COLOR,
        padx=5,
        pady=5
    )
    process_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Configure text tags for styling with better visibility
    process_output.tag_configure("header", foreground="#81A1C1", font=("Consolas", 11, "bold"))
    process_output.tag_configure("info", foreground="#88C0D0")
    process_output.tag_configure("error", foreground="#BF616A")
    process_output.tag_configure("system", foreground="#EBCB8B")
    process_output.tag_configure("success", foreground="#A3BE8C")
    process_output.tag_configure("final", foreground="#A3BE8C", font=("Consolas", 10, "bold"))
    
    # Function to update the UI for file changes
    def update_ui_for_file_changes():
        global file_changes_detected, monitored_count
        
        monitored_var.set(f"Files Detected: {monitored_count}")
        
        if file_changes_detected:
            status_var.set("Status: New files detected. Can be processed.")
        else:
            status_var.set("Status: Monitoring files. No new files detected yet.")
    
    # Define button actions with cleaner toggle logic
    def toggle_monitoring():
        global monitor_running, monitored_count, processing_running, processor_thread, processed_count
        
        if not monitor_running:
            # Start monitoring
            control_btn.config(text="Stop Monitoring")
            progress_var.set(0)  # Reset progress
            start_monitor_thread(
                monitor_output,
                progress_var,
                update_ui_for_file_changes
            )
            status_var.set("Status: Monitoring active")
        else:
            # Stop monitoring
            control_btn.config(text="Start Monitoring")
            stop_monitor_thread(progress_var)
            status_var.set("Status: Monitoring stopped")
            
            # Automatically start processing if files were detected
            if file_changes_detected:
                process_documents_with_ui_updates()
    
    # Extract processing logic to make toggle function cleaner
    def process_documents_with_ui_updates():
        global processor_thread, processing_running, processed_count
        
        if processing_running or (processor_thread is not None and processor_thread.is_alive()):
            monitor_output.insert(tk.END, "⚠️ Document processing is already running.\n", "system")
            return
        
        # Check if we have the required packages
        if not HAS_PROCESSING:
            process_output.insert(tk.END, "❌ Required libraries for document processing are missing.\n", "error")
            process_output.insert(tk.END, "Please install: faiss-cpu, numpy, tqdm, requests, and markitdown\n", "info")
            return
        
        # Update UI
        status_var.set("Status: Processing documents...")
        progress_var.set(0)
        
        # Start processing in a separate thread
        processor_thread = threading.Thread(target=process_worker)
        processor_thread.daemon = True
        processor_thread.start()
        
        # Start updating output
        update_output(process_output, process_output_queue, last_line_var)
        
        # Animate progress bar while processing
        animate_progress_bar(progress_var, 0)
        
        # Monitor the thread to update UI when done
        check_process_done(progress_var)
    
    # Function to animate progress bar - simplified
    def animate_progress_bar(progress_var, value):
        if processing_running and value <= 95:
            # Slowly increase progress
            new_value = min(value + 0.5, 95)
            progress_var.set(new_value)
            # Schedule next update
            monitor_tab.after(200, lambda: animate_progress_bar(progress_var, new_value))
    
    # Function to check if processing is done - simplified
    def check_process_done(progress_var):
        global processor_thread, processing_running, processed_count
        
        if processor_thread and not processor_thread.is_alive() and processing_running:
            processing_running = False
            progress_var.set(100)  # Set progress to 100%
            status_var.set(f"Status: Processing complete - {processed_count} file(s) processed")
            processed_var.set(f"Files Processed: {processed_count}")
            process_output.insert(tk.END, "🎉 Document processing completed.\n", "success")
        elif processing_running:
            # Check again in 100ms
            monitor_tab.after(100, lambda: check_process_done(progress_var))
    
    # Connect the button actions
    control_btn.config(command=toggle_monitoring)
    
    # Initial welcome messages with improved formatting
    monitor_output.insert(tk.END, "=== File Monitor ===\n", "header")
    monitor_output.insert(tk.END, "Welcome to the Document Intelligence System\n\n", "info")
    monitor_output.insert(tk.END, "• Click 'Start Monitoring' to begin tracking file access.\n", "info")
    monitor_output.insert(tk.END, "• Detected files will be added to visited_files.json.\n", "info")
    monitor_output.insert(tk.END, "• Click 'Stop Monitoring' to stop tracking and process files automatically.\n", "info")
    monitor_output.insert(tk.END, f"• Supported file types: {', '.join(SUPPORTED_EXTENSIONS)}\n\n", "info")
    
    process_output.insert(tk.END, "=== Document Processor ===\n", "header")
    process_output.insert(tk.END, "Intelligent Document Processing\n\n", "info")
    process_output.insert(tk.END, "• Documents will be processed automatically when monitoring is stopped.\n", "info")
    process_output.insert(tk.END, "• Files will be analyzed, chunked, and embedded for semantic search.\n", "info")
    process_output.insert(tk.END, "• Processing logs will be displayed here in real-time.\n\n", "info")
    
    if not HAS_PROCESSING:
        process_output.insert(tk.END, "⚠️ WARNING: Required libraries for document processing are missing.\n", "error")
        process_output.insert(tk.END, "Please install: faiss-cpu, numpy, tqdm, requests, and markitdown\n", "info")
    
    # Check if visited_files.json already has files
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                visited_files = json.load(f)
                if visited_files:
                    global file_changes_detected
                    file_changes_detected = True
                    update_ui_for_file_changes()
                    monitor_output.insert(tk.END, f"📂 Found {len(visited_files)} entries in visited_files.json.\n", "info")
                    monitor_output.insert(tk.END, "These will be processed automatically when monitoring is stopped.\n\n", "info")
        except Exception:
            pass
    
    # Return the tab and callbacks
    callbacks = {
        'is_monitor_running': is_monitor_running,
        'is_processing_running': is_processing_running,
        'stop_monitoring': lambda: stop_monitor_thread(progress_var) if monitor_running else None
    }
    
    return monitor_tab, callbacks