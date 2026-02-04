import os, re
from PyPDF2 import PdfReader

def wildcard_to_regex(pattern: str) -> str:
    escaped = re.escape(pattern)
    return escaped.replace(r"\*", ".*").replace(r"\?", ".")

def parse_query(query: str):
    """
    Split query into tokens and operators.
    Supports !and, !or. Default between words is !and.
    """
    tokens = []
    for word in query.split():
        if word.lower() in ("!and", "!or"):
            tokens.append(word.lower())
        else:
            tokens.append(word)
    return tokens

def match_text(text: str, query: str) -> bool:
    """
    Match text against query using !and / !or operators.
    Implicit !and between tokens if no operator specified.
    """
    tokens = parse_query(query)
    result = None
    operator = None

    for token in tokens:
        if token in ("!and", "!or"):
            operator = token
        else:
            regex = wildcard_to_regex(token)
            match = re.search(regex, text, re.IGNORECASE) is not None

            if result is None:
                result = match
            else:
                if operator == "!and" or operator is None:
                    result = result and match
                elif operator == "!or":
                    result = result or match
            operator = None  # reset after use
    print(match, result)
    return result if result is not None else False

def find_pdfs(folder_path: str, query: str):
    matches = []

    for filename in os.listdir(folder_path):
        if not filename.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(folder_path, filename)

        try:
            reader = PdfReader(pdf_path)
            full_text = ""

            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + " "

            if full_text and match_text(full_text, query):
                matches.append(pdf_path)

        except Exception as e:
            print(f"Could not read {pdf_path}: {e}")

    return matches

# --- Example ---
if __name__ == "__main__":
    folder = r"data"
    query = "Period !and 06-Jan-26 !or 12-Jan-26"
    results = find_pdfs(folder, query)
    for pdf in results:
        print(pdf)
