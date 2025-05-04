# EAG-Session-7-Assignment     --- Document Intelligence System

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

<pre>Console cleared
=== DocumentAnalyst Agent Started ===
Agent is ready to process input. Type text or load a document file.
Processing input: what is enchanted library
[22:41:14] [agent] Starting agent loop...
[22:41:14] [agent] Connection established, creating session...
[22:41:14] [agent] Session created, initializing...
[22:41:16] [agent] MCP session initialized
[22:41:16] [Available tools:] ['search_documents', 'add', 'sqrt', 'subtract', 'multiply', 'divide', 'power', 'cbrt', 'factorial', 'log', 'remainder', 'sin', 'cos', 'tan', 'mine', 'create_thumbnail', 'strings_to_chars_to_int', 'int_list_to_exponential_sum', 'fibonacci_numbers']
[22:41:16] [agent] 19 tools loaded
[22:41:16] [loop] Step 1 started
[22:41:16] [agent] User input: what is enchanted library
[22:41:17] [perception] Intent: find information, Tool hint: Search
[22:41:17] [memory] Retrieved 0 relevant memories
[22:41:19] [plan] Plan generated: FUNCTION_CALL: search_documents|query="enchanted library"
[22:41:21] [tool] search_documents returned: ['Enchanted Library. Her grandmother often spoke of its wonders, and Emily dreamed of one day exploring its mystical halls. One sunny afternoon, while rummaging through her grandmother’s attic, Emily stumbled upon a hidden compartment in an old wooden chest. Inside, she found an intricately designed key with shimmering runes and a tag that read: “To awaken the magic, unlock the heart.” Excited, Emily hurried to the library. The once-majestic building was overgrown with ivy and vines. The grand wooden doors were locked tight, but Emily’s key fit perfectly. As she turned it, the doors creaked open with a magical shimmer, revealing a world of enchantment. Inside, the library was bathed in a golden glow. Dust motes danced in the air, and the shelves, though covered in cobwebs, seemed to whisper secrets. Emily approached the grand hall, where a towering book, bound in gold and silver, rested on a pedestal. The book was locked with a complex mechanism. Suddenly, a soft, rustling sound caught Emily’s attention. Out of the shadows emerged a glowing, ancient book named Barnaby. He floated gracefully, his cover adorned with ornate patterns and twinkling stars. “Welcome, Emily,” Barnaby said in a warm, echoing voice. “I’ve been waiting for someone with a pure heart to restore the magic. I am Barnaby, the guardian of this library.” Emily’s eyes widened. “You know my name?” Barnaby chuckled softly. “I know all who seek the magic of stories. To restore the library, we must unlock the heart of its enchantment. But first, we need to navigate the\n[Source: Small-Stories-in-English-learnenglishteam.com_.pdf, Chunk ID: Small-Stories-in-English-learnenglishteam.com_4,path: D:\\Programming\\EAG V1\\pdf\\Small-Stories-in-English-learnenglishteam.com.pdf]', 'was hidden behind a sliding wall. Finn used the code to unlock the wall, revealing a dazzling array of gold coins, jewels, and precious artifacts. At the center of the treasure was a beautifully crafted chest with a plaque that read: “To the bravest of hearts.” As Finn marveled at the treasure, Captain Squawk appeared again, fluttering with joy. “Ye’ve done it, young adventurer! Ye’ve found the lost treasure of Pi-Rate Island! But remember, true treasure is not just gold and jewels—it’s the adventure and courage ye showed.” Finn agreed, realizing that the journey itself had been as valuable as the treasure. He returned to Seaside with stories of his adventure and the lost treasure. The villagers celebrated his bravery, and Pi-Rate Island became a symbol of adventure and discovery. Main Idea: The true treasure lies not just in gold and jewels, but in the courage and adventure experienced along the journey. The Enchanted Library In the charming village of Willowbrook, there was once a grand library known as the Enchanted Library, famous for its magical books and timeless tales. Sadly, a dark spell had sealed the library for years, leaving its wonders dormant and forgotten. Emily, a bright and adventurous girl with a love for stories, had always been captivated by the tales of the Enchanted Library. Her grandmother often spoke of its wonders, and Emily dreamed of one day exploring its mystical halls. One sunny afternoon, while rummaging through her grandmother’s attic, Emily stumbled upon a hidden compartment in an old wooden chest. Inside,\n[Source: Small-Stories-in-English-learnenglishteam.com_.pdf, Chunk ID: Small-Stories-in-English-learnenglishteam.com_3,path: D:\\Programming\\EAG V1\\pdf\\Small-Stories-in-English-learnenglishteam.com.pdf]', 'this library.” Emily’s eyes widened. “You know my name?” Barnaby chuckled softly. “I know all who seek the magic of stories. To restore the library, we must unlock the heart of its enchantment. But first, we need to navigate the challenges that have kept it hidden for so long.” Barnaby led Emily through the labyrinthine library, filled with hidden passages and secret rooms. They ventured into the Grand Gallery, a room with walls that were covered in moving paintings and glowing constellations. Each painting depicted scenes from famous stories, but they seemed frozen in time. Emily’s first challenge was to solve a puzzle to unlock a hidden door. The door was adorned with a riddle: “I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?” Barnaby hovered beside her, his pages fluttering with anticipation. Emily thought deeply and answered, “An echo!” The door creaked open, revealing a hidden chamber filled with old, dusty scrolls. In this chamber, Emily and Barnaby discovered a journal with clues to the library’s secrets. The journal spoke of three enchanted relics that held the key to awakening the magic: a mystical feather, a golden quill, and an ancient scroll. Their journey led them to the Hall of Relics, where the feather was hidden. The room was filled with enchanted traps and magical barriers. Emily had to navigate through a series of moving platforms and shifting walls. With Barnaby’s guidance and encouragement, Emily’s quick thinking and bravery helped her retrieve\n[Source: Small-Stories-in-English-learnenglishteam.com_.pdf, Chunk ID: Small-Stories-in-English-learnenglishteam.com_5,path: D:\\Programming\\EAG V1\\pdf\\Small-Stories-in-English-learnenglishteam.com.pdf]', 'I am used by almost every person. What am I?” “I can be cracked, made, told, and played. What am I?” “I have keys but open no locks. I have space but no room. You can enter but not go outside. What am I?” With each correct answer, the chest’s lock clicked open. When Emily finally opened the chest, a brilliant light burst forth, filling the library with warmth and magic. The once-sleeping books awoke, their pages rustling with excitement, and the enchantment of the library was restored. Emily and Barnaby watched as the library transformed into a vibrant, magical place. The books floated gently from the shelves, and the air was filled with the soft whispers of stories coming to life. Emily was given the special gift of bringing stories to life simply by reading them aloud. Returning to Willowbrook, Emily shared her adventure with the villagers, who marveled at the revived Enchanted Library. The library’s doors were now open to everyone, and the village celebrated the magic of stories and the wonders of imagination. Emily’s adventure taught her that the true magic of the library was not just in its books but in the belief and curiosity that could awaken even the deepest enchantments. Main Idea: The true magic of stories is unlocked through curiosity, courage, and a belief in the power of imagination. The Brave Little Squirrel In the heart of the forest, there was a brave little squirrel named Nutty. Nutty was known for his boundless energy and adventurous spirit. One day,\n[Source: Small-Stories-in-English-learnenglishteam.com_.pdf, Chunk ID: Small-Stories-in-English-learnenglishteam.com_7,path: D:\\Programming\\EAG V1\\pdf\\Small-Stories-in-English-learnenglishteam.com.pdf]', 'sought to harness its power for himself. Without it, the village’s magic was waning, and its connection to the outside world was slowly disappearing. Determined to help, Ella set out with Lorian and his friends. The first stop was the Enchanted Forest, a mystical part of the forest filled with ancient trees and hidden paths. Ella was introduced to the village’s wise old wizard, Alaric, who had once been a guardian of the Heartstone but had lost his memory and powers after the crystal was stolen. Alaric, though frail and forgetful, gave Ella a magical compass that would guide her to the sorcerer’s lair. He also shared a clue: “The Heartstone lies where shadows dance and the moonlight sings.” Ella and Lorian ventured deeper into the forest, encountering a series of magical challenges. They navigated through the Whispering Woods, where the trees whispered secrets and misdirected travelers. They befriended a mischievous sprite named Flicker who offered to guide them through the maze of thorns in exchange for a promise of friendship. Flicker led them to the Moonlit Glade, where shadows seemed to come alive. The sorcerer’s lair was hidden in a cave behind a waterfall. As they approached, Ella noticed that the cave was guarded by enchanted creatures—a giant, shimmering serpent with scales like mirrors. Ella used her wits to distract the serpent by creating illusions with her lantern and using the magical compass to find a hidden path around it. Inside the cave, she found the Heartstone atop a pedestal, glowing faintly in the dim\n[Source: Small-Stories-in-English-learnenglishteam.com_.pdf, Chunk ID: Small-Stories-in-English-learnenglishteam.com_14,path: D:\\Programming\\EAG V1\\pdf\\Small-Stories-in-English-learnenglishteam.com.pdf]']
[22:41:24] [loop] Step 2 started
[22:41:24] [agent] User input: Original task: what is enchanted library
Previous output: ['Enchanted Library. Her grandmother often spoke of its wonders, and Emily dreamed of one day exploring its mystical halls. One sunny afternoon, while rummaging through her grandmother’s attic, Emily stumbled upon a hidden compartment in an old wooden chest. Inside, she found an intricately designed key with shimmering runes and a tag that read: “To awaken the magic, unlock the heart.” Excited, Emily hurried to the library. The once-majestic building was overgrown with ivy and vines. The grand wooden doors were locked tight, but Emily’s key fit perfectly. As she turned it, the doors creaked open with a magical shimmer, revealing a world of enchantment. Inside, the library was bathed in a golden glow. Dust motes danced in the air, and the shelves, though covered in cobwebs, seemed to whisper secrets. Emily approached the grand hall, where a towering book, bound in gold and silver, rested on a pedestal. The book was locked with a complex mechanism. Suddenly, a soft, rustling sound caught Emily’s attention. Out of the shadows emerged a glowing, ancient book named Barnaby. He floated gracefully, his cover adorned with ornate patterns and twinkling stars. “Welcome, Emily,” Barnaby said in a warm, echoing voice. “I’ve been waiting for someone with a pure heart to restore the magic. I am Barnaby, the guardian of this library.” Emily’s eyes widened. “You know my name?” Barnaby chuckled softly. “I know all who seek the magic of stories. To restore the library, we must unlock the heart of its enchantment. But first, we need to navigate the\n[Source: Small-Stories-in-English-learnenglishteam.com_.pdf, Chunk ID: Small-Stories-in-English-learnenglishteam.com_4,path: D:\\Programming\\EAG V1\\pdf\\Small-Stories-in-English-learnenglishteam.com.pdf]', 'was hidden behind a sliding wall. Finn used the code to unlock the wall, revealing a dazzling array of gold coins, jewels, and precious artifacts. At the center of the treasure was a beautifully crafted chest with a plaque that read: “To the bravest of hearts.” As Finn marveled at the treasure, Captain Squawk appeared again, fluttering with joy. “Ye’ve done it, young adventurer! Ye’ve found the lost treasure of Pi-Rate Island! But remember, true treasure is not just gold and jewels—it’s the adventure and courage ye showed.” Finn agreed, realizing that the journey itself had been as valuable as the treasure. He returned to Seaside with stories of his adventure and the lost treasure. The villagers celebrated his bravery, and Pi-Rate Island became a symbol of adventure and discovery. Main Idea: The true treasure lies not just in gold and jewels, but in the courage and adventure experienced along the journey. The Enchanted Library In the charming village of Willowbrook, there was once a grand library known as the Enchanted Library, famous for its magical books and timeless tales. Sadly, a dark spell had sealed the library for years, leaving its wonders dormant and forgotten. Emily, a bright and adventurous girl with a love for stories, had always been captivated by the tales of the Enchanted Library. Her grandmother often spoke of its wonders, and Emily dreamed of one day exploring its mystical halls. One sunny afternoon, while rummaging through her grandmother’s attic, Emily stumbled upon a hidden compartment in an old wooden chest. Inside,\n[Source: Small-Stories-in-English-learnenglishteam.com_.pdf, Chunk ID: Small-Stories-in-English-learnenglishteam.com_3,path: D:\\Programming\\EAG V1\\pdf\\Small-Stories-in-English-learnenglishteam.com.pdf]', 'this library.” Emily’s eyes widened. “You know my name?” Barnaby chuckled softly. “I know all who seek the magic of stories. To restore the library, we must unlock the heart of its enchantment. But first, we need to navigate the challenges that have kept it hidden for so long.” Barnaby led Emily through the labyrinthine library, filled with hidden passages and secret rooms. They ventured into the Grand Gallery, a room with walls that were covered in moving paintings and glowing constellations. Each painting depicted scenes from famous stories, but they seemed frozen in time. Emily’s first challenge was to solve a puzzle to unlock a hidden door. The door was adorned with a riddle: “I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?” Barnaby hovered beside her, his pages fluttering with anticipation. Emily thought deeply and answered, “An echo!” The door creaked open, revealing a hidden chamber filled with old, dusty scrolls. In this chamber, Emily and Barnaby discovered a journal with clues to the library’s secrets. The journal spoke of three enchanted relics that held the key to awakening the magic: a mystical feather, a golden quill, and an ancient scroll. Their journey led them to the Hall of Relics, where the feather was hidden. The room was filled with enchanted traps and magical barriers. Emily had to navigate through a series of moving platforms and shifting walls. With Barnaby’s guidance and encouragement, Emily’s quick thinking and bravery helped her retrieve\n[Source: Small-Stories-in-English-learnenglishteam.com_.pdf, Chunk ID: Small-Stories-in-English-learnenglishteam.com_5,path: D:\\Programming\\EAG V1\\pdf\\Small-Stories-in-English-learnenglishteam.com.pdf]', 'I am used by almost every person. What am I?” “I can be cracked, made, told, and played. What am I?” “I have keys but open no locks. I have space but no room. You can enter but not go outside. What am I?” With each correct answer, the chest’s lock clicked open. When Emily finally opened the chest, a brilliant light burst forth, filling the library with warmth and magic. The once-sleeping books awoke, their pages rustling with excitement, and the enchantment of the library was restored. Emily and Barnaby watched as the library transformed into a vibrant, magical place. The books floated gently from the shelves, and the air was filled with the soft whispers of stories coming to life. Emily was given the special gift of bringing stories to life simply by reading them aloud. Returning to Willowbrook, Emily shared her adventure with the villagers, who marveled at the revived Enchanted Library. The library’s doors were now open to everyone, and the village celebrated the magic of stories and the wonders of imagination. Emily’s adventure taught her that the true magic of the library was not just in its books but in the belief and curiosity that could awaken even the deepest enchantments. Main Idea: The true magic of stories is unlocked through curiosity, courage, and a belief in the power of imagination. The Brave Little Squirrel In the heart of the forest, there was a brave little squirrel named Nutty. Nutty was known for his boundless energy and adventurous spirit. One day,\n[Source: Small-Stories-in-English-learnenglishteam.com_.pdf, Chunk ID: Small-Stories-in-English-learnenglishteam.com_7,path: D:\\Programming\\EAG V1\\pdf\\Small-Stories-in-English-learnenglishteam.com.pdf]', 'sought to harness its power for himself. Without it, the village’s magic was waning, and its connection to the outside world was slowly disappearing. Determined to help, Ella set out with Lorian and his friends. The first stop was the Enchanted Forest, a mystical part of the forest filled with ancient trees and hidden paths. Ella was introduced to the village’s wise old wizard, Alaric, who had once been a guardian of the Heartstone but had lost his memory and powers after the crystal was stolen. Alaric, though frail and forgetful, gave Ella a magical compass that would guide her to the sorcerer’s lair. He also shared a clue: “The Heartstone lies where shadows dance and the moonlight sings.” Ella and Lorian ventured deeper into the forest, encountering a series of magical challenges. They navigated through the Whispering Woods, where the trees whispered secrets and misdirected travelers. They befriended a mischievous sprite named Flicker who offered to guide them through the maze of thorns in exchange for a promise of friendship. Flicker led them to the Moonlit Glade, where shadows seemed to come alive. The sorcerer’s lair was hidden in a cave behind a waterfall. As they approached, Ella noticed that the cave was guarded by enchanted creatures—a giant, shimmering serpent with scales like mirrors. Ella used her wits to distract the serpent by creating illusions with her lantern and using the magical compass to find a hidden path around it. Inside the cave, she found the Heartstone atop a pedestal, glowing faintly in the dim\n[Source: Small-Stories-in-English-learnenglishteam.com_.pdf, Chunk ID: Small-Stories-in-English-learnenglishteam.com_14,path: D:\\Programming\\EAG V1\\pdf\\Small-Stories-in-English-learnenglishteam.com.pdf]']
What should I do next?
[22:41:26] [perception] Intent: no intent detected; continue current task, Tool hint: N/A
[22:41:28] [memory] Retrieved 3 relevant memories
[22:41:31] [plan] Plan generated: FINAL_ANSWER: [The Enchanted Library was a grand library in the charming village of Willowbrook, famous for its magical books and timeless tales. Sadly, a dark spell had sealed the library for years, leaving its wonders dormant and forgotten. It was restored by Emily, a bright and adventurous girl.] [Source: Small-Stories-in-English-learnenglishteam.com_.pdf, Chunk ID: Small-Stories-in-English-learnenglishteam.com_3,path: D:\\Programming\\EAG V1\\pdf\\Small-Stories-in-English-learnenglishteam.com.pdf]
[22:41:31] [agent] Extracted Chunk ID: Small-Stories-in-English-learnenglishteam.com__3
[22:41:31] [agent] Extracted chunk data: was hidden behind a sliding wall. Finn used the code to unlock the wall, revealing a dazzling array of gold coins, jewels, and precious artifacts. At the center of the treasure was a beautifully crafted chest with a plaque that read: “To the bravest of hearts.” As Finn marveled at the treasure, Captain Squawk appeared again, fluttering with joy. “Ye’ve done it, young adventurer! Ye’ve found the lost treasure of Pi-Rate Island! But remember, true treasure is not just gold and jewels—it’s the adventure and courage ye showed.” Finn agreed, realizing that the journey itself had been as valuable as the treasure. He returned to Seaside with stories of his adventure and the lost treasure. The villagers celebrated his bravery, and Pi-Rate Island became a symbol of adventure and discovery. Main Idea: The true treasure lies not just in gold and jewels, but in the courage and adventure experienced along the journey. The Enchanted Library In the charming village of Willowbrook, there was once a grand library known as the Enchanted Library, famous for its magical books and timeless tales. Sadly, a dark spell had sealed the library for years, leaving its wonders dormant and forgotten. Emily, a bright and adventurous girl with a love for stories, had always been captivated by the tales of the Enchanted Library. Her grandmother often spoke of its wonders, and Emily dreamed of one day exploring its mystical halls. One sunny afternoon, while rummaging through her grandmother’s attic, Emily stumbled upon a hidden compartment in an old wooden chest. Inside,
[22:41:31] [agent] Opened source file: D:\\Programming\\EAG V1\\pdf\\Small-Stories-in-English-learnenglishteam.com_.pdf
[22:41:39] [agent] ✅ FINAL RESULT: FINAL_ANSWER: [The Enchanted Library was a grand library in the charming village of Willowbrook, famous for its magical books and timeless tales. Sadly, a dark spell had sealed the library for years, leaving its wonders dormant and forgotten. It was restored by Emily, a bright and adventurous girl.] [Source: Small-Stories-in-English-learnenglishteam.com_.pdf, Chunk ID: Small-Stories-in-English-learnenglishteam.com_3,path: D:\\Programming\\EAG V1\\pdf\\Small-Stories-in-English-learnenglishteam.com.pdf]
[22:41:39] [agent] Agent session complete.</pre>
