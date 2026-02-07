"""
Document Loader - Extract text from various file formats for summarization
Supports: .txt, .pdf, .docx
"""

import os


def extract_text_from_file(filepath: str) -> str:
    """
    Extract plain text from a file. Supports .txt, .pdf, .docx.
    
    Args:
        filepath: Path to the file
        
    Returns:
        Extracted text content
        
    Raises:
        ValueError: If file type is not supported or extraction fails
    """
    if not os.path.isfile(filepath):
        raise ValueError(f"File not found: {filepath}")
    
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext == ".txt":
        return _read_txt(filepath)
    elif ext == ".pdf":
        return _read_pdf(filepath)
    elif ext in (".docx", ".doc"):
        return _read_docx(filepath)
    else:
        raise ValueError(
            f"Unsupported file type: {ext}. Supported: .txt, .pdf, .docx"
        )


def _read_txt(filepath: str) -> str:
    """Read plain text file."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _read_pdf(filepath: str) -> str:
    """Extract text from PDF using PyPDF2."""
    try:
        import PyPDF2
    except ImportError:
        raise ValueError(
            "PDF support requires PyPDF2. Install with: pip install PyPDF2"
        )
    
    text_parts = []
    with open(filepath, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text_parts.append(content)
    
    return "\n\n".join(text_parts) if text_parts else ""


def _read_docx(filepath: str) -> str:
    """Extract text from Word document."""
    try:
        from docx import Document
    except ImportError:
        raise ValueError(
            "Word document support requires python-docx. Install with: pip install python-docx"
        )
    
    doc = Document(filepath)
    return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
