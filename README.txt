           *~~~\_._/~~~*       
          *~  ( o o )  ~*    
         *~   (  -  )   ~*  
        **~~~o("===")o~~~**   
       *\/\/\/\/\/\/\/\/\/ *

            BRYNN-P
      Netnoodle Web Scraper  

# Netnoodle – Web Scraper & Wordlist Helper.

Netnoodle is a small Python3 tool used for scraping web pages or local files and extracting readable text as well as generating simple wordlists geared toward CTFs, recon, and general tinkering.
It focuses on being easy to run from the terminal while handling a few common document types out of the box. 

## Features

- Scrape a URL and auto-detect basic document types (HTML, XML-ish, JSON, plain text) from HTTP responses.  
- Load local files and parse supported types (txt, csv, html/htm, docx) into plain text.
- Build a deduplicated wordlist from extracted text with configurable:
  - minimum and maximum token length,
  - maximum number of lines (cap).
- Save raw text and generated wordlists to files with user-chosen filenames.  
- Includes error messages if optional libraries (python-magic, python-docx) are missing or a file/url cannot be parsed.  

## Requirements

- Python 3.x  
- The Python packages listed in `requirements.txt`:

  - `beautifulsoup4`  
  - `lxml`  
  - `requests`  
  - `python-docx`  
  - `python-magic-bin` (for Windows) or python-magic on some platforms  
  - Plus standard support packages like urllib3, certifi, etc.

Install everything with:

pip install -r requirements.txt

text

## Installation

1. Clone or download this repository.  
2. (Optional but recommended) create and activate a virtual environment.  
3. Install dependencies:

pip install -r requirements.txt

text

## Usage

Run Netnoodle from the project directory:

python Netnoodle.py

text

You’ll see a simple menu:

1. **Scrape a URL (auto-detect)** – fetch a URL, detect the document type, extract text, then:
   - preview the first 300 characters,
   - optionally save the full text to a file,
   - or generate a wordlist from the scraped text.  

2. **Load local file (detect & parse)** – provide a local path to a supported file (txt/csv/html/docx), then:
   - preview the first 300 characters,
   - optionally save parsed text,
   - or generate a wordlist from that content. 

3. **Quit** – exit the tool.

When generating a wordlist, you can customize:

- minimum token length (default 4),  
- maximum token length (default 12),  
- maximum number of lines/tokens to keep (default 50000). 

You can then choose to save the wordlist (default filename `wordlist.txt`) or just preview the first 50 tokens in the terminal.  

## Notes and limitations

- Local file parsing currently supports:
  - Plain text / CSV
  - HTML / HTM
  - DOCX (requires python-docx) 
- Other formats (like PDF and more complex binary types) will raise a clear “no parser implemented” error for now.
- python-magic / python-magic-bin improves file type detection, but the script falls back to using file extensions if it’s not available.
- This tool is intended for legal and ethical use only: CTF challenges, lab environments, or systems where you have explicit permission to scrape and analyze content.
