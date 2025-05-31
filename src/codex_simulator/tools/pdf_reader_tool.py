import os
from typing import List, Dict, Any, Union # Added Union
from crewai.tools import BaseTool # Changed import
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

class PDFReaderTool(BaseTool):
    name: str = "PDF Reader Tool"
    description: str = (
        "Reads text content from a PDF file and can break it down into smaller chunks. "
        "Input to 'read_pdf' should be the path to the PDF file. "
        "Input to 'break_down_pdf' should be a dictionary with 'pdf_path', "
        "'chunk_size' (optional, default 1000), and 'chunk_overlap' (optional, default 200)."
    )

    def _run(self, argument: Union[str, Dict[str, Any]]) -> str:
        """
        Main entry point for the tool.
        If argument is a string, it's treated as a pdf_path for reading.
        If argument is a dict, it checks for 'action' key: 'read' or 'chunk'.
        """
        if isinstance(argument, str):
            # Default action is to read the PDF if only path is provided
            return self.read_pdf(pdf_path=argument)
        elif isinstance(argument, dict):
            action = argument.get("action", "read") # Default to read
            pdf_path = argument.get("pdf_path")

            if not pdf_path:
                return "Error: 'pdf_path' must be provided in the input dictionary."
            if not os.path.exists(pdf_path):
                return f"Error: PDF file not found at path: {pdf_path}"
            if not pdf_path.lower().endswith(".pdf"):
                return f"Error: Invalid file type. Expected a .pdf file, got: {pdf_path}"

            if action == "read":
                return self.read_pdf(pdf_path=pdf_path)
            elif action == "chunk":
                chunk_size = argument.get("chunk_size", 1000)
                chunk_overlap = argument.get("chunk_overlap", 200)
                chunks = self.break_down_pdf(pdf_path=pdf_path, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
                if isinstance(chunks, str) and chunks.startswith("Error:"):
                    return chunks
                return f"PDF broken down into {len(chunks)} chunks. Content of chunks:\n" + "\n---\n".join(chunks)
            else:
                return "Error: Invalid action. Must be 'read' or 'chunk'."
        else:
            return "Error: Invalid argument type. Must be a string (pdf_path) or a dictionary."

    def read_pdf(self, pdf_path: str) -> str:
        """Reads and returns the full text content of a PDF file."""
        if not os.path.exists(pdf_path):
            return f"Error: PDF file not found at path: {pdf_path}"
        if not pdf_path.lower().endswith(".pdf"):
            return f"Error: Invalid file type. Expected a .pdf file, got: {pdf_path}"
            
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            if not text.strip():
                return "Warning: No text could be extracted from the PDF. It might be image-based or empty."
            return text
        except Exception as e:
            return f"Error reading PDF file {pdf_path}: {str(e)}"

    def break_down_pdf(self, pdf_path: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> Union[List[str], str]:
        """Reads a PDF, extracts text, and breaks it into smaller chunks."""
        full_text = self.read_pdf(pdf_path)
        if full_text.startswith("Error:") or full_text.startswith("Warning:"):
            return full_text # Return error or warning from read_pdf

        if not full_text.strip(): # Check if full_text is empty after successful read
            return "Error: PDF content is empty, cannot break down."

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
        chunks = text_splitter.split_text(full_text)
        if not chunks:
            return "Warning: Could not break down the PDF content into chunks. The content might be too short or an issue occurred."
        return chunks

