import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import queue
import time
import asyncio
import os
import json
from pathlib import Path
import datetime
from perception import extract_perception
from memory import MemoryManager, MemoryItem
from decision import generate_plan
from action import execute_tool
import re
import pyautogui

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    HAS_MCP = True
except ImportError:
    HAS_MCP = False

# Maximum steps in the agent's reasoning loop
MAX_STEPS = 3

class AgentTab:
    def __init__(self, parent):
        self.parent = parent
        self.tab = ttk.Frame(parent)
        self.agent = None
        self.output_queue = queue.Queue()
        self.running = False
        self.setup_ui()
        
    def setup_ui(self):
        # Top pane for agent controls
        control_frame = ttk.LabelFrame(self.tab, text="Agent Controls")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Agent name
        name_frame = ttk.Frame(control_frame)
        name_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(name_frame, text="Agent Name:").pack(side=tk.LEFT, padx=5)
        self.agent_name = tk.StringVar(value="DocumentAnalyst")
        name_entry = ttk.Entry(name_frame, textvariable=self.agent_name, width=20)
        name_entry.pack(side=tk.LEFT, padx=5)
        
        # Start/Stop button
        self.start_stop_btn = ttk.Button(
            name_frame, 
            text="Start Agent", 
            command=self.toggle_agent
        )
        self.start_stop_btn.pack(side=tk.LEFT, padx=20)
        
        # Status label
        self.status_var = tk.StringVar(value="Status: Ready")
        status_label = ttk.Label(
            name_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 9, "italic")
        )
        status_label.pack(side=tk.RIGHT, padx=10)
        
        # Console output - directly in the main tab
        console_frame = ttk.Frame(self.tab)
        console_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Console label
        ttk.Label(console_frame, text="Agent Console:").pack(anchor=tk.W, pady=5)
        
        # Console text area
        self.console_text = scrolledtext.ScrolledText(
            console_frame,
            wrap=tk.WORD,
            height=15,
            bg="#282a36",
            fg="#f8f8f2",
            font=("Consolas", 10)
        )
        self.console_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Configure tags for console text
        self.console_text.tag_configure("info", foreground="#8be9fd")
        self.console_text.tag_configure("perception", foreground="#50fa7b")
        self.console_text.tag_configure("decision", foreground="#bd93f9")
        self.console_text.tag_configure("action", foreground="#ff79c6")
        self.console_text.tag_configure("memory", foreground="#f1fa8c")
        self.console_text.tag_configure("error", foreground="#ff5555")
        
        # Bottom pane for input
        input_frame = ttk.LabelFrame(self.tab, text="Agent Input")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Input controls
        self.input_text = scrolledtext.ScrolledText(
            input_frame,
            wrap=tk.WORD,
            height=4,
            font=("Segoe UI", 10)
        )
        self.input_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Input buttons
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        send_btn = ttk.Button(
            btn_frame,
            text="Send Input",
            command=self.send_input
        )
        send_btn.pack(side=tk.LEFT, padx=5)
        
        load_file_btn = ttk.Button(
            btn_frame,
            text="Load File",
            command=self.load_file
        )
        load_file_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(
            btn_frame,
            text="Clear Console",
            command=self.clear_console
        )
        clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # Instructions text
        ttk.Label(
            btn_frame, 
            text="Type text for agent to analyze or load a document file", 
            font=("Segoe UI", 9, "italic")
        ).pack(side=tk.TOP, pady=(5, 0))
        
        # Initial welcome message
        self.log_to_console("=== Document Intelligence Agent ===\n", "info")
        self.log_to_console("Agent ready to process documents and text.\n\n", "info")
        self.log_to_console("• Start the agent using the 'Start Agent' button.\n", "info")
        self.log_to_console("• Type text or load documents for analysis.\n", "info")
        self.log_to_console("• Agent will perceive, decide, and act on the content.\n", "info")
        
    def toggle_agent(self):
        """Start or stop the agent"""
        if not self.running:
            self.start_agent()
        else:
            self.stop_agent()
    
    def start_agent(self):
        """Initialize and start the agent"""
        try:
            agent_name = self.agent_name.get().strip()
            if not agent_name:
                messagebox.showerror("Error", "Please enter an agent name")
                return
            
            # Update UI
            self.log_to_console(f"Initializing agent '{agent_name}'...\n", "info")
            self.start_stop_btn.config(text="Stop Agent")
            self.status_var.set("Status: Running")
            self.running = True
            
            # Clear console
            self.clear_console()
            self.log_to_console(f"=== {agent_name} Agent Started ===\n", "info")
            self.log_to_console("Agent is ready to process input. Type text or load a document file.\n", "info")
            
            # Start output monitoring
            self.start_output_monitor()
        except Exception as e:
            self.log_to_console(f"Error starting agent: {str(e)}\n", "error")
            self.running = False
            self.start_stop_btn.config(text="Start Agent")
            self.status_var.set("Status: Error")
    
    def stop_agent(self):
        """Stop the running agent"""
        if not self.running:
            return
            
        self.log_to_console("Stopping agent...\n", "info")
        self.running = False
        self.agent = None
        
        # Update UI
        self.start_stop_btn.config(text="Start Agent")
        self.status_var.set("Status: Stopped")
        self.log_to_console("Agent stopped\n", "info")
    
    def send_input(self):
        """Send text input to the agent for processing"""
        if not self.running:
            messagebox.showinfo("Agent Not Running", "Please start the agent first")
            return
            
        # Get input text
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo("Empty Input", "Please enter some text to process")
            return
            
        # Disable input while processing
        self.input_text.config(state=tk.DISABLED)
        self.log_to_console(f"Processing input: {text[:50]}{'...' if len(text) > 50 else ''}\n", "info")
        
        # Start processing in a background thread
        threading.Thread(target=self.run_agent_thread, args=(text,), daemon=True).start()
    
    def run_agent_thread(self, text):
        """Run the agent loop in a background thread"""
        try:
            # Create and run event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.agent_loop(text))
        except Exception as e:
            self.output_queue.put(("error", f"Error in agent thread: {str(e)}\n"))
        finally:
            # Re-enable input when done
            self.tab.after(0, lambda: self.input_text.config(state=tk.NORMAL))
    
    def load_file(self):
        """Load a document file for processing"""
        if not self.running or not self.agent:
            messagebox.showinfo("Agent Not Running", "Please start the agent first")
            return
            
        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Select Document",
            filetypes=[
                ("Text Files", "*.txt"),
                ("Markdown", "*.md"),
                ("PDF Files", "*.pdf"),
                ("Word Documents", "*.docx"),
                ("All Files", "*.*")
            ]
        )
        
        if not file_path:
            return
            
        # Check if file exists
        path = Path(file_path)
        if not path.exists():
            messagebox.showerror("Error", f"File not found: {file_path}")
            return
            
        # Load and process based on file type
        self.log_to_console(f"Loading file: {path.name}\n", "info")
        
        # Handle different file types
        if path.suffix.lower() in ['.txt', '.md']:
            # Simple text file
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert("1.0", content)
                self.log_to_console(f"Loaded text file ({len(content)} chars). Click 'Send Input' to process.\n", "info")
            except Exception as e:
                self.log_to_console(f"Error loading file: {str(e)}\n", "error")
        else:
            # For other file types we'd need converters
            try:
                # Try using a simple extraction if possible
                from markitdown import MarkItDown
                converter = MarkItDown()
                result = converter.convert(file_path)
                content = result.text_content
                
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert("1.0", content)
                self.log_to_console(f"Converted document to text ({len(content)} chars). Click 'Send Input' to process.\n", "info")
            except ImportError:
                self.log_to_console("Document conversion requires the markitdown package.\n", "error")
                self.log_to_console("Please install it with: pip install markitdown\n", "info")
            except Exception as e:
                self.log_to_console(f"Error converting document: {str(e)}\n", "error")
    
    def clear_console(self):
        """Clear the console output"""
        self.console_text.delete("1.0", tk.END)
        self.log_to_console("Console cleared\n", "info")
    
    def log_to_console(self, message, tag=None):
        """Add a message to the console with optional tag"""
        self.console_text.insert(tk.END, message, tag)
        self.console_text.see(tk.END)
    
    def start_output_monitor(self):
        """Start monitoring the output queue for messages"""
        try:
            # Process all pending messages
            while True:
                try:
                    tag, message = self.output_queue.get_nowait()
                    self.log_to_console(message, tag)
                except queue.Empty:
                    break
                    
            # Schedule next update
            if self.running:
                self.tab.after(100, self.start_output_monitor)
        except Exception as e:
            print(f"Error monitoring output: {e}")
            # Try again later
            if self.running:
                self.tab.after(500, self.start_output_monitor)
    
    def log_ui(self, stage: str, msg: str):
        """Log a message to the UI console with appropriate tag"""
        now = datetime.datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{now}] [{stage}] {msg}\n"
        
        # Map stages to UI tags
        tag_map = {
            "agent": "info",
            "perception": "perception",
            "memory": "memory",
            "plan": "decision",
            "tool": "action",
            "error": "error",
            "loop": "info"
        }
        tag = tag_map.get(stage, "info")
        
        # Add to output queue (thread-safe)
        self.output_queue.put((tag, log_msg))

    async def agent_loop(self, user_input: str):
        """Core agent loop that matches the functionality of agent.py"""
        try:
            self.log_ui("agent", "Starting agent loop...")
            
            # Initialize MCP client if available
            if not HAS_MCP:
                self.log_ui("error", "MCP library not available. Please install it with: pip install mcp-client")
                return
                
            server_params = StdioServerParameters(
                command="python",
                args=["example3.py"],
                cwd=os.getcwd()
            )

            try:
                async with stdio_client(server_params) as (read, write):
                    self.log_ui("agent", "Connection established, creating session...")
                    try:
                        async with ClientSession(read, write) as session:
                            self.log_ui("agent", "Session created, initializing...")
    
                            try:
                                await session.initialize()
                                self.log_ui("agent", "MCP session initialized")
                                # Your reasoning, planning, perception etc. would go here
                                tools = await session.list_tools()
                                self.log_ui("Available tools:", [t.name for t in tools.tools])

                                # Get available tools
                                tools_result = await session.list_tools()
                                tools = tools_result.tools
                                tool_descriptions = "\n".join(
                                    f"- {tool.name}: {getattr(tool, 'description', 'No description')}" 
                                    for tool in tools
                                )

                                self.log_ui("agent", f"{len(tools)} tools loaded")

                                memory = MemoryManager()
                                session_id = f"session-{int(time.time())}"
                                query = user_input  # Store original intent
                                step = 0

                                while step < MAX_STEPS and self.running:
                                    self.log_ui("loop", f"Step {step + 1} started")
                                    self.log_ui("agent", f"User input: {user_input}")
                                    perception = extract_perception(user_input)
                                    self.log_ui("perception", f"Intent: {perception.intent}, Tool hint: {perception.tool_hint}")

                                    retrieved = memory.retrieve(query=user_input, top_k=3, session_filter=session_id)
                                    self.log_ui("memory", f"Retrieved {len(retrieved)} relevant memories")

                                    plan = generate_plan(perception, retrieved, tool_descriptions=tool_descriptions)
                                    self.log_ui("plan", f"Plan generated: {plan}")

                                    if plan.startswith("FINAL_ANSWER:"):
                                        # Extract source file information if it exists
                                        self.add_open_file_button(plan)
                                        # source_file = None
                                        # chunk_id = None
                                        # if "Source:" in plan:
                                        #     try:
                                        #         # Extract the source file from the format "Source: filename, Chunk ID: chunk_id"
                                        #         source_info = plan.split("Source:")[1].strip()
                                        #         if "," in source_info:
                                        #             source_parts = source_info.split(",")
                                        #             source_file = source_parts[0].strip()
                                        #             self.log_ui("agent", f"Source file: {source_file}")
                                        #             # Extract chunk ID if it exists
                                        #             for part in source_parts[1:]:
                                        #                 if "Chunk ID:" in part or "ChunkID:" in part or "Chunk:" in part:
                                        #                     chunk_id = part.split(":", 1)[1].strip()
                                        #                     break
                                        #         else:
                                        #             source_file = source_info.strip()
                                                
                                        #         # Remove any trailing characters
                                        #         if " " in source_file:
                                        #             source_file = source_file.split(" ")[0].strip()
                                                
                                        #         # The source file might be in the documents folder
                                        #         if not os.path.exists(source_file) and os.path.exists(os.path.join("documents", source_file)):
                                        #             source_file = os.path.join("documents", source_file)
                                        #     except Exception as e:
                                        #         self.log_ui("error", f"Error parsing source file: {str(e)}")
                                        
                                        # Log the final result - keep the FINAL_RESULT format as requested
                                        self.log_ui("agent", f"✅ FINAL RESULT: {plan}")
                                        
                                        # If we found a source file, add a button to open it
                                        break
                                        

                                    try:
                                        result = await execute_tool(session, tools, plan)
                                        self.log_ui("tool", f"{result.tool_name} returned: {result.result}")

                                        memory.add(MemoryItem(
                                            text=f"Tool call: {result.tool_name} with {result.arguments}, got: {result.result}",
                                            type="tool_output",
                                            tool_name=result.tool_name,
                                            user_query=user_input,
                                            tags=[result.tool_name],
                                            session_id=session_id
                                        ))

                                        user_input = f"Original task: {query}\nPrevious output: {result.result}\nWhat should I do next?"

                                    except Exception as e:
                                        self.log_ui("error", f"Tool execution failed: {e}")
                                        break

                                    step += 1
                                    
                                
                            except Exception as e:
                                self.log_ui("error", f"Session initialization error: {str(e)}")
                                
                    except Exception as e:
                        self.log_ui("error", f"Session creation error: {str(e)}")
                        
            except Exception as e:
                self.log_ui("error", f"Connection error: {str(e)}")
                
        except Exception as e:
            self.log_ui("error", f"Overall error: {str(e)}")
            
        self.log_ui("agent", "Agent session complete.")
        
        
        
        # Update UI state when done
        if self.running:
            self.tab.after(0, self.update_ui_after_completion)
    
    def update_ui_after_completion(self):
        """Update UI after agent completes execution"""
        self.start_stop_btn.config(text="Start Agent")
        self.status_var.set("Status: Ready")
        self.running = False

    def load_metadata(self):
        """Load metadata from the FAISS index to find chunks by ID"""
        try:
            metadata_path = os.path.join("faiss_index", "metadata.json")
            if not os.path.exists(metadata_path):
                return None
                
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            return metadata
        except Exception as e:
            self.log_ui("error", f"Error loading metadata: {str(e)}")
            return None
    
    def find_chunk_by_id(self, chunk_id):
        """Find a specific chunk by its ID in the metadata"""
        metadata = self.load_metadata()
        if not metadata:
            return None
            
        for item in metadata:
            if item.get("chunk_id") == chunk_id:
                return item
        return None
    
    
    def add_open_file_button(self, plan):
        """Open the source file based on extracted path and extract chunk ID"""
        try:
            import re, os
            from tkinter import messagebox

            # Extract the path
            path_match = re.search(r'path:\s*(.+)', plan)
            if path_match:
                file_path = path_match.group(1).strip()
                file_path = file_path[:-1] if file_path.endswith("]") else file_path

                # Extract the chunk ID
                chunk_match = re.search(r'Chunk ID:\s*([^\],\n]+)', plan)
                chunk_id = chunk_match.group(1).strip() if chunk_match else None

                if chunk_id:
                    self.log_ui("agent", f"Extracted Chunk ID: {chunk_id}")
                else:
                    self.log_ui("warning", "Chunk ID not found.")
                    
                with open("faiss_index/metadata.json", 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            
                for entry in metadata:
                    if entry.get("chunk_id") == chunk_id:
                        data=entry.get("chunk")

                self.log_ui("agent", f"Extracted chunk data: {data}")
                # Open the file
                if not os.path.exists(file_path):
                    self.log_ui("error", f"File not found: {file_path}")
                    messagebox.showerror("Error", f"File not found:\n{file_path}")
                    return

                os.startfile(file_path)
                self.log_ui("agent", f"Opened source file: {file_path}")
                
                time.sleep(5)  # Wait for app to load; increase if needed

                print("Sending Ctrl+F...")
                pyautogui.hotkey('ctrl', 'f')
                time.sleep(1)

                print(f"Typing search text: {data}")
                pyautogui.typewrite(data[5:20], interval=0.05)
                time.sleep(0.5)

                pyautogui.press('enter')  # Trigger search if needed
                print("Search initiated.")
            else:
                self.log_ui("error", "No path found in the provided plan.")
                messagebox.showerror("Error", "No path found in the provided plan.")
        except Exception as e:
            self.log_ui("error", f"Error opening source file: {str(e)}")
            
    
    
    def open_chunk_viewer(self, chunk_info):
        """Open a new window displaying the chunk content with highlighting"""
        try:
            # Create a new window
            viewer = tk.Toplevel(self.tab)
            viewer.title(f"Chunk Viewer - {chunk_info.get('doc', 'Unknown')} - {chunk_info.get('chunk_id', 'Unknown')}")
            viewer.geometry("800x600")
            
            # Add content area
            frame = ttk.Frame(viewer)
            frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Header info
            header_text = f"Document: {chunk_info.get('doc', 'Unknown')}\n"
            header_text += f"Chunk ID: {chunk_info.get('chunk_id', 'Unknown')}\n"
            header_text += f"Source File: {chunk_info.get('file_path', 'Unknown')}\n"
            header_text += "\n" + "-" * 80 + "\n\n"
            
            # Content text area
            content_text = scrolledtext.ScrolledText(
                frame,
                wrap=tk.WORD,
                font=("Consolas", 10),
                bg="#f5f5f5",
                fg="#333333"
            )
            content_text.pack(fill=tk.BOTH, expand=True)
            
            # Insert header
            content_text.insert(tk.END, header_text, "header")
            content_text.tag_configure("header", font=("Segoe UI", 10, "bold"))
            
            # Insert chunk content with highlighting
            content_text.insert(tk.END, chunk_info.get("chunk", "No content available"))
            
            # Add button to open original file
            file_path = chunk_info.get("file_path")
            if file_path and os.path.exists(file_path):
                def open_original():
                    os.startfile(file_path)
                
                ttk.Button(
                    frame,
                    text=f"Open Original File: {os.path.basename(file_path)}",
                    command=open_original
                ).pack(pady=10)
            
        except Exception as e:
            self.log_ui("error", f"Error opening chunk viewer: {str(e)}")

def create_agent_tab(parent):
    """Create and return the agent tab"""
    agent_tab_instance = AgentTab(parent)
    
    # Return the tab and callbacks dictionary
    callbacks = {
        'is_running': lambda: agent_tab_instance.running,
        'stop': agent_tab_instance.stop_agent
    }
    
    return agent_tab_instance.tab, callbacks