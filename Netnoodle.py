#!/usr/bin/env python3
"""
What we have here is a simple web scraper that I have built using python3. 
There are a few uses for it, however it is geared towards CTF challenges and creating wordlists.
This is my first full word list generator/scraper so please be kind :)
In built it around the hack the box python learning modlue as well as IBM's guided web project and i have expended on it as well as Chat GPT for guidence and troubleshooting.
This is partially vibecoded, however it was not a copy and paste job.
Feel free to use and modify it as you see fit.
overall i hope you find it useful!

"""
import requests
from bs4 import BeautifulSoup
import re
import json
import sys
from pathlib import Path

def print_banner():
    banner = r"""
           *~~~\_._/~*       
          *~  ( o o )  ~*    
         *~   (  -  )   ~*  
        **~~~o("===")o~~~**   
       *\/\/\/\/\/\/\/\/\/ *

            BRYNN-P
      Netnoodle Web Scraper            
"""
    print(banner)

# for local imports 
try: 
    import magic
except Exception:
    magic = None 
    print("python_magic libary not found or not installed, file type detection unavailable\ncheck requirements.txt for more info")

try: 
    from docx import Document
except Exception:
    Document = None 
    print("docx libary not found or not installed, dox file parsing unavailable\ncheck requirements.txt for more info")

# url helpers

def normalize_url(url):
    url = url.strip()
    if not re.match(r"^https?://", url):
        url = "http://" + url
    return url

def fetch_url(url: str, timeout: int = 10):
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        return r
    except requests.exceptions.RequestException as e:
        print(f"error fetching {url}: {e}")
        return None
    
def validate_url(url):
    if not url.strip():
        print("Error: URL cannot be empty")
        return False

    pattern = re.compile(r"^https?://[^\s/$.?#].[^\s]*$")
    if not pattern.match(url):
        print("Error: Invalid URL format.....must start with http:// or https://")
        return False
    return True

def url_check(url):
    if not url.startswith("http"):
        url = "http://" + url
    if not url.endswith("/"):
        url = url + "/"
    return url

"""
wordlist helpers guided by chat gpt

"""

# ---------- Wordlist helpers ----------
def extract_candidate_words(text: str, min_alpha_len=3):
    """
    Extract candidate tokens from text. Returns a deduped set.
    Keeps alphanum tokens, allows small numeric tokens of length >=3.
    """
    tokens = re.findall(r"[A-Za-z0-9'’\-_]+", text)
    cleaned = set()
    for t in tokens:
        t2 = t.strip("'’-_").strip()
        if not t2:
            continue
        letters = re.sub(r"[^A-Za-z]", "", t2)
        if len(letters) < min_alpha_len:
            # allow numeric tokens like 2023
            if not re.match(r"^\d{3,}$", t2):
                continue
        cleaned.add(t2)
    return cleaned

def build_simple_wordlist(text: str, min_len=4, max_len=12, cap=50000):
    """
    Build a basic deduped wordlist from text.
    Returns a list limited by cap.
    """
    cand = extract_candidate_words(text)
    out = []
    for w in sorted(cand):
        if len(w) < min_len or len(w) > max_len:
            continue
        out.append(w)
        if len(out) >= cap:
            break
    return out


"""
helpers for saveing text and wordlists 
main functions below added by chat gpt

"""
def save_text_to_file(text: str, filename: str):
    try:
        with open(filename, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"Saved text to {filename}")
        return True
    except Exception as e:
        print(f"[!] Failed to save text: {e}")
        return False

def save_wordlist_to_file(wordlist: list, filename: str):
    try:
        with open(filename, "w", encoding="utf-8") as fh:
            for w in wordlist:
                fh.write(w + "\n")
        print(f"Wrote {len(wordlist)} lines to {filename}")
        return True
    except Exception as e:
        print(f"[!] Failed to save wordlist: {e}")
        return False

"""
Local file type detection and parsing 

"""
def detect_local_file_type(filepath: str) -> str:
    """
    Return a mime-type string for a local file.
    Uses python-magic (if available) and falls back to extension guesses.
    """
    p = Path(filepath)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    if magic:
        try:
            m = magic.from_file(str(p), mime=True)
            if m:
                return m
        except Exception:
            # fall through to suffix-based guess
            pass
    # fallback by extension
    ext = p.suffix.lower()
    return {
        ".txt": "text/plain",
        ".csv": "text/plain",
        ".html": "text/html",
        ".htm": "text/html",
        ".xml": "application/xml",
        ".json": "application/json",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".pdf": "application/pdf"
    }.get(ext, "application/octet-stream")


def parse_local_file_to_text(filepath: str) -> str:
    """
    Parse local file to plain text.
    Supports: text, html, docx (requires python-docx).
    Raises informative errors for unsupported formats.
    """
    mtype = detect_local_file_type(filepath)
    p = Path(filepath)

    # plain text / csv
    if mtype.startswith("text") or p.suffix.lower() in {".txt", ".csv"}:
        with open(p, "r", encoding="utf-8", errors="ignore") as fh:
            return fh.read()

    # html
    if mtype == "text/html" or p.suffix.lower() in {".html", ".htm"}:
        with open(p, "r", encoding="utf-8", errors="ignore") as fh:
            soup = BeautifulSoup(fh, "html.parser")
            return soup.get_text(separator="\n")

    # docx
    if mtype == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" or p.suffix.lower() == ".docx":
        if Document is None:
            raise RuntimeError("python-docx is not installed. Run: pip install python-docx")
        doc = Document(str(p))
        # join paragraphs with newlines
        return "\n".join([para.text for para in doc.paragraphs])

    # placeholder: pdf and other types not yet implemented
    raise RuntimeError(f"No parser implemented for mime type: {mtype} (file: {filepath})")


"""
this sections is used to detect the document type from HTTP responses.
I will expand on this in future releases to include more document types. 
But for now this is what we have. 
The below function was giving me errors until Chat GPT helped me fix it :)
"""

def detect_doc_type_response(response) -> str:
    ctype = (response.headers.get("Content-Type") or "").lower()
    head = ""

    try:
        # decode first chunk of body for simple heuristics
        head = response.content[:4096].decode("utf-8", errors="ignore").lstrip()
    except Exception:
        head = ""

    # JSON heuristics
    if "application/json" in ctype or head.startswith("{") or head.startswith("["):
        return "json"

    # XML heuristics: xml header or xml-like tags (but not html)
    if "xml" in ctype or head.startswith("<?xml") or re.search(r"<\w+:?\w+>", head):
        if re.search(r"<html\b", head, re.IGNORECASE):
            return "html"
        return "xml"

    # HTML heuristics
    if "html" in ctype or re.search(r"<html\b", head, re.IGNORECASE):
        return "html"

    # default fallback
    return "text"

"""
this section is used for parsing response to Plain Text
still many improvements to be made here.
"""

def parse_response_to_text(response, doc_type: str) -> str:
    if doc_type == "html":
        soup = BeautifulSoup(response.content, "html.parser")
        return soup.get_text(separator="\n")
    if doc_type == "xml":
        soup = BeautifulSoup(response.content, "xml")
        return soup.get_text(separator="\n")
    if doc_type == "json":
        try:
            return json.dumps(response.json(), ensure_ascii=False, indent=2)
        except Exception:
            return response.text
    return response.text

"""
a much more simplified main function with the auto detection added in. 
this saved me many lines of if statments, but ironically the code keeps getting longer lol 
"""

def main():
    last_text = None

    while True:
        print("\nMain menu:")
        print("1) Scrape a URL (auto-detect)         - fetch and extract text")
        print("2) Load local file (detect & parse)  - docx/html/txt")
        print("3) Quit")
        choice = input("Choose (1/2/3): ").strip()

        if choice == "3":
            print("Bye.")
            return

        if choice == "1":
            url = input("Enter URL (include http:// or https://): ").strip()
            url = normalize_url(url)
            if not validate_url(url):
                continue
            response = fetch_url(url)
            if not response:
                continue
            doc_type = detect_doc_type_response(response)
            print(f"Detected document type: {doc_type}")
            text = parse_response_to_text(response, doc_type)
            # store for further operations
            last_text = text
            print("\n--- preview (first 300 chars) ---")
            print(text[:300])

            # post-scrape action menu
            print("\nPost-scrape options:")
            print("a) Save scraped text to file")
            print("b) Build simple wordlist from scraped text")
            print("c) Return to main menu")
            action = input("Choose (a/b/c): ").strip().lower()
            if action == "a":
                out = input("Filename to save scraped text (default scraped.txt): ").strip() or "scraped.txt"
                save_text_to_file(text, out)
            elif action == "b":
                min_len = int(input("Min token length (default 4): ").strip() or "4")
                max_len = int(input("Max token length (default 12): ").strip() or "12")
                cap = int(input("Cap lines (default 50000): ").strip() or "50000")
                wl = build_simple_wordlist(text, min_len=min_len, max_len=max_len, cap=cap)
                print(f"Generated {len(wl)} tokens.")
                save = input("Save wordlist? (y/N): ").strip().lower() == "y"
                if save:
                    out = input("Wordlist filename (default wordlist.txt): ").strip() or "wordlist.txt"
                    save_wordlist_to_file(wl, out)
                else:
                    print("Preview first 50 tokens:")
                    for t in wl[:50]:
                        print(t)

        elif choice == "2":
            path = input("Enter local file path: ").strip()
            try:
                text = parse_local_file_to_text(path)
            except Exception as e:
                print(f"[!] Error parsing file: {e}")
                continue
            last_text = text
            print("\n--- preview (first 300 chars) ---")
            print(text[:300])

            print("\nOptions for local file:")
            print("a) Save parsed text to file")
            print("b) Build simple wordlist from parsed text")
            print("c) Return to main menu")
            action = input("Choose (a/b/c): ").strip().lower()
            if action == "a":
                out = input("Filename to save parsed text (default parsed.txt): ").strip() or "parsed.txt"
                save_text_to_file(text, out)
            elif action == "b":
                min_len = int(input("Min token length (default 4): ").strip() or "4")
                max_len = int(input("Max token length (default 12): ").strip() or "12")
                cap = int(input("Cap lines (default 50000): ").strip() or "50000")
                wl = build_simple_wordlist(text, min_len=min_len, max_len=max_len, cap=cap)
                print(f"Generated {len(wl)} tokens.")
                save = input("Save wordlist? (y/N): ").strip().lower() == "y"
                if save:
                    out = input("Wordlist filename (default wordlist.txt): ").strip() or "wordlist.txt"
                    save_wordlist_to_file(wl, out)
                else:
                    print("Preview first 50 tokens:")
                    for t in wl[:50]:
                        print(t)
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    print_banner()
    main()
