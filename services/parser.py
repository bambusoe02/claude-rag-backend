from fastapi import UploadFile
import pypdf
from io import BytesIO
from typing import Optional

async def parse_document(file: UploadFile) -> str:
    """Parse PDF, TXT, or MD file to text"""
    
    content = await file.read()
    
    if file.filename.endswith('.pdf'):
        return parse_pdf(content)
    elif file.filename.endswith('.md'):
        return parse_markdown(content)
    elif file.filename.endswith('.txt'):
        return parse_text(content)
    elif file.filename.endswith('.docx'):
        return parse_docx(content)
    else:
        raise ValueError(f"Unsupported file type: {file.filename}")

def parse_pdf(content: bytes) -> str:
    """Extract text from PDF"""
    try:
        reader = pypdf.PdfReader(BytesIO(content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error parsing PDF: {str(e)}")

def parse_markdown(content: bytes) -> str:
    """Parse markdown file"""
    try:
        md_text = content.decode('utf-8')
        return md_text
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            return content.decode('latin-1')
        except Exception as e:
            raise ValueError(f"Error decoding markdown file: {str(e)}")

def parse_text(content: bytes) -> str:
    """Parse plain text file"""
    try:
        return content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            return content.decode('latin-1')
        except Exception as e:
            raise ValueError(f"Error decoding text file: {str(e)}")

def parse_docx(content: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        from docx import Document
        doc = Document(BytesIO(content))
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except ImportError:
        raise ValueError("python-docx package required for DOCX files. Install with: pip install python-docx")
    except Exception as e:
        raise ValueError(f"Error parsing DOCX: {str(e)}")

