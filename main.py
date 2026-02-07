import re
from pathlib import Path
from typing import List
import fitz  # PyMuPDF
from time import time

LOGICAL_OPS = {"!and", "!or"}
pdfs = 0

# ---------- QUERY PRECOMPILATION ----------

def compile_query(query: str, exact_phrase: bool = False) -> list:
    compiled = []
    operator = "!and"

    if exact_phrase:
        # Split only on operators
        tokens = []
        buffer = []
        for word in query.split():
            word_l = word.lower()
            if word_l in LOGICAL_OPS:
                if buffer:
                    tokens.append(("!and", " ".join(buffer)))
                    buffer = []
                tokens.append((word_l, None))  # placeholder for operator
            else:
                buffer.append(word)
        if buffer:
            tokens.append(("!and", " ".join(buffer)))

        # Correctly assign operator to next token
        final_compiled = []
        operator = "!and"
        for op, tok in tokens:
            if tok is None:
                operator = op  # operator token, applies to next
                continue
            regex_pattern = r"\b" + re.escape(tok).replace(r"\*", ".*").replace(r"\?", ".") + r"\b"
            final_compiled.append((operator, re.compile(regex_pattern, re.IGNORECASE)))
            operator = "!and"  # reset after use
        return final_compiled

    # exact_phrase=False: split every word
    for token in query.split():
        token_l = token.lower()
        if token_l in LOGICAL_OPS:
            operator = token_l
            continue
        regex_pattern = r"\b" + re.escape(token).replace(r"\*", ".*").replace(r"\?", ".") + r"\b"
        compiled.append((operator, re.compile(regex_pattern, re.IGNORECASE)))
        operator = "!and"

    return compiled


def match_text(text: str, compiled_query: list) -> bool:
    """
    Evaluate precompiled query against text.
    """
    result = None
    for operator, regex in compiled_query:
        matched = bool(regex.search(text))
        if result is None:
            result = matched
        elif operator == "!and":
            result &= matched
        else:  # !or
            result |= matched
    return bool(result)


# ---------- PDF SCANNING ----------

def iter_pdfs(folder_path: str):
    """Yield all PDF files in a folder."""
    global pdfs

    folder = Path(folder_path)
    for file in folder.iterdir():
        if file.is_file() and file.suffix.lower() == ".pdf":
            pdfs += 1
            yield file


def find_pdfs(folder_path: str, query: str, exact_phrase: bool = True) -> List[str]:
    """
    Scan PDFs and return paths where query matches anywhere.
    """
    compiled_query = compile_query(query, exact_phrase=exact_phrase)
    matches: list[str] = []

    for pdf_path in iter_pdfs(folder_path):
        try:
            doc = fitz.open(pdf_path)
            full_text = " ".join(page.get_text() for page in doc)
            doc.close()
            if full_text and match_text(full_text, compiled_query):
                matches.append(str(pdf_path))
        except Exception as exc:
            print(f"Could not read {pdf_path}: {exc}")

    return matches


# ---------- EXAMPLE ----------

if __name__ == "__main__":
    folder = "data"  # dir containing pdfs
    query = "Report No. 02 !or India"

    start = time()
    results = find_pdfs(folder, query)

    print("\nMatched PDFs:", len(results), "/", pdfs)
    print("\n".join(results))
    print(f"Time: {time()-start:.2f}s")
