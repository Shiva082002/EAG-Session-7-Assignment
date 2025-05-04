# EAG-Session-8-Assignment     --- Document Intelligence System

A comprehensive document monitoring, tracking, and intelligence system that tracks file access across your system and provides intelligent finding capabilities on user query.

## Features

- 📁 **File Monitoring**  
  Automatically tracks file access and modifications across your system with support for various document types (PDF, DOCX, XLSX, etc.).

- 🔍 **Document Intelligence**  
  Processes tracked documents to extract meaningful insights and information.

- 💾 **Persistent Storage**  
  Stores tracking data in JSON format for easy access and for documnet processing.

- 📊 **File Metadata Management**  
  Captures and organizes metadata about accessed files including size, timestamps, and paths.

- 🧠 **Agent-Based Architecture**  
  Implements a flexible, agent-based system for finding specific document according to user query.

- 📱 **Tab-Based UI**  
  Provides a user-friendly interface with separate tabs for monitoring, files, and agent interactions for user query.

## 🗂️ Project Structure

### Core Components

- **File Monitor** (`monitor_tab.py`)  
  Watches file system events and records document access across specified directories and process those documents

- **Document Processor** (`document_intelligence_system.py`)  
  Main core file to interacte with all these three ui that are `monitor_tab.py` ,  `files_tab.py`  and `agent_tab.py`.

- **File Manager** (`files_tab.py`)  
  Manages file metadata and provides an interface for file operations.

- **Agent System** (`agent_tab.py`)  
  Handles intelligent processing through an agent-based architecture for performing query on those documents



### Supporting Components

- **Memory Management** (`memory.py`)  
  Provides persistent storage mechanisms for the system.

- **Perception Layer** (`perception.py`)  
  Handles document understanding and feature extraction.

- **Decision Layer** (`decision.py`)  
  Determines actions based on document analysis.

- **Action Layer** (`action.py`)  
  Executes operations on documents.

- **Models** (`models.py`)  
  Defines data structures used throughout the system.

## 📊 Data Storage

The system uses several JSON files for data persistence:

- `visited_files.json`: Records file access history
- `metadata.json`: Stores document metadata information
- Additional cache files for document indexing

## 🔮 Supported File Types

The system monitors and processes various document types including:

- PDF documents (`.pdf`)
- Microsoft Office files (`.docx`, `.xlsx`, `.pptx`)
- Text files (`.txt`, `.md`)
- CSV files (`.csv`)
- And more!

## How to Run the Code

### 1. Install `uv`

First, install [uv](https://github.com/astral-sh/uv), a fast Python package manager:

```bash
pip install uv
```
### 2.  Run the Telegram Bot

Once uv is installed, you can run the bot using:

```bash
uv run document_intelligence_system.py

```


## Logs
