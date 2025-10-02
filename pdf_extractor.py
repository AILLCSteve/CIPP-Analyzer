#!/usr/bin/env python3
"""
CIPP PDF Text Extraction Service
Provides proper PDF text extraction for the CIPP Analyzer application
"""

import sys
import json
import logging
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import tempfile
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Try to import PDF processing libraries
try:
    import PyPDF2
    PDF_LIBRARY = "PyPDF2"
    logger.info("Using PyPDF2 for PDF processing")
except ImportError:
    try:
        import pdfplumber
        PDF_LIBRARY = "pdfplumber"
        logger.info("Using pdfplumber for PDF processing")
    except ImportError:
        try:
            from pdfminer.high_level import extract_text
            PDF_LIBRARY = "pdfminer"
            logger.info("Using pdfminer for PDF processing")
        except ImportError:
            PDF_LIBRARY = None
            logger.error("No PDF processing library found. Please install: pip install PyPDF2 pdfplumber pdfminer.six")

def extract_text_pypdf2(pdf_path):
    """Extract text using PyPDF2"""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text.strip():
                    text += f"\n--- PAGE {page_num + 1} ---\n{page_text}\n"

        logger.info(f"PyPDF2 extracted {len(text)} characters from {len(pdf_reader.pages)} pages")
        return text.strip()
    except Exception as e:
        logger.error(f"PyPDF2 extraction failed: {e}")
        raise

def extract_text_pdfplumber(pdf_path):
    """Extract text using pdfplumber (better for tables and layout)"""
    text = ""
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text += f"\n--- PAGE {page_num + 1} ---\n{page_text}\n"

                # Also try to extract tables
                tables = page.extract_tables()
                if tables:
                    text += f"\n--- TABLES ON PAGE {page_num + 1} ---\n"
                    for table_num, table in enumerate(tables):
                        text += f"\nTable {table_num + 1}:\n"
                        for row in table:
                            if row:
                                row_text = " | ".join([cell or "" for cell in row])
                                text += f"{row_text}\n"

        logger.info(f"pdfplumber extracted {len(text)} characters from {len(pdf.pages)} pages")
        return text.strip()
    except Exception as e:
        logger.error(f"pdfplumber extraction failed: {e}")
        raise

def extract_text_pdfminer(pdf_path):
    """Extract text using pdfminer"""
    try:
        from pdfminer.high_level import extract_text
        text = extract_text(pdf_path)
        logger.info(f"pdfminer extracted {len(text)} characters")
        return text.strip()
    except Exception as e:
        logger.error(f"pdfminer extraction failed: {e}")
        raise

def extract_pdf_text(pdf_path):
    """Extract text from PDF using the best available method"""
    if not PDF_LIBRARY:
        raise Exception("No PDF processing library available. Please install: pip install PyPDF2 pdfplumber pdfminer.six")

    logger.info(f"Extracting text from: {pdf_path}")

    # Try different extraction methods in order of preference
    methods = []
    if PDF_LIBRARY == "pdfplumber":
        methods = [extract_text_pdfplumber, extract_text_pypdf2, extract_text_pdfminer]
    elif PDF_LIBRARY == "PyPDF2":
        methods = [extract_text_pypdf2, extract_text_pdfplumber, extract_text_pdfminer]
    else:  # pdfminer
        methods = [extract_text_pdfminer, extract_text_pdfplumber, extract_text_pypdf2]

    last_error = None
    for method in methods:
        try:
            text = method(pdf_path)
            if text and len(text.strip()) > 50:  # Minimum reasonable text length
                logger.info(f"Successfully extracted text using {method.__name__}")
                return text
        except Exception as e:
            last_error = e
            logger.warning(f"Method {method.__name__} failed: {e}")
            continue

    raise Exception(f"All PDF extraction methods failed. Last error: {last_error}")

@app.route('/extract_pdf', methods=['POST'])
def extract_pdf_endpoint():
    """API endpoint to extract text from PDF"""
    try:
        data = request.get_json()

        if not data or 'pdf_data' not in data:
            return jsonify({'error': 'No PDF data provided'}), 400

        # Decode base64 PDF data
        try:
            pdf_bytes = base64.b64decode(data['pdf_data'])
        except Exception as e:
            return jsonify({'error': f'Invalid base64 data: {e}'}), 400

        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(pdf_bytes)
            temp_path = temp_file.name

        try:
            # Extract text
            extracted_text = extract_pdf_text(temp_path)

            if not extracted_text or len(extracted_text.strip()) < 10:
                return jsonify({'error': 'No readable text found in PDF'}), 400

            # Clean up the text
            cleaned_text = clean_extracted_text(extracted_text)

            logger.info(f"Successfully extracted {len(cleaned_text)} characters")

            return jsonify({
                'success': True,
                'text': cleaned_text,
                'length': len(cleaned_text),
                'method': PDF_LIBRARY
            })

        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except:
                pass

    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return jsonify({'error': str(e)}), 500

def clean_extracted_text(text):
    """Clean and format extracted text"""
    if not text:
        return ""

    # Remove excessive whitespace
    lines = []
    for line in text.split('\n'):
        cleaned_line = ' '.join(line.split())  # Remove extra spaces
        if cleaned_line:  # Only keep non-empty lines
            lines.append(cleaned_line)

    # Join lines with single newlines
    cleaned = '\n'.join(lines)

    # Remove excessive newlines (more than 2 consecutive)
    import re
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

    return cleaned.strip()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'pdf_library': PDF_LIBRARY,
        'libraries_available': {
            'PyPDF2': 'PyPDF2' in sys.modules or check_import('PyPDF2'),
            'pdfplumber': 'pdfplumber' in sys.modules or check_import('pdfplumber'),
            'pdfminer': check_import('pdfminer.high_level')
        }
    })

def check_import(module_name):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False

if __name__ == '__main__':
    if not PDF_LIBRARY:
        print("ERROR: No PDF processing library found!")
        print("Please install one of the following:")
        print("  pip install PyPDF2")
        print("  pip install pdfplumber")
        print("  pip install pdfminer.six")
        sys.exit(1)

    print(f"Starting CIPP PDF Extraction Service using {PDF_LIBRARY}")
    print("Service will be available at: http://localhost:5000")
    print("Health check: http://localhost:5000/health")

    app.run(host='localhost', port=5000, debug=False)