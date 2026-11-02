
import fitz
from pathlib import Path


# =================================
# EXTRACT TEXT FROM PDF
# =================================

def extract_pdf_text(file_path):

    extracted_text = []

    try:

        document = fitz.open(file_path)

        for page_number, page in enumerate(document, start=1):

            page_text = page.get_text()

            if page_text.strip():

                extracted_text.append(
                    f"\n--- Page {page_number} ---\n"
                    + page_text
                )

        document.close()

        return "\n".join(extracted_text)

    except Exception as error:

        raise RuntimeError(
            f"Could not process PDF: {error}"
        ) from error


# =================================
# EXTRACT TEXT FROM TXT
# =================================

def extract_txt_text(file_path):

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return file.read()

    except UnicodeDecodeError as error:

        raise RuntimeError(
            "The TXT file does not use UTF-8 encoding."
        ) from error

    except OSError as error:

        raise RuntimeError(
            f"Could not read TXT file: {error}"
        ) from error


# =================================
# COMMON DOCUMENT PROCESSOR
# =================================

def extract_document_text(file_path):

    file_path = Path(file_path)

    extension = file_path.suffix.lower()

    if extension == ".pdf":

        return extract_pdf_text(file_path)

    elif extension == ".txt":

        return extract_txt_text(file_path)

    else:

        raise ValueError(
            "Unsupported file type. Upload PDF or TXT files."
        )


# =================================
# PROCESS STREAMLIT UPLOADED FILE
# =================================

def extract_uploaded_document(uploaded_file):

    file_name = uploaded_file.name

    extension = Path(file_name).suffix.lower()

    file_bytes = uploaded_file.getvalue()

    if extension == ".pdf":

        try:

            document = fitz.open(
                stream=file_bytes,
                filetype="pdf"
            )

            extracted_text = []

            for page_number, page in enumerate(
                document,
                start=1
            ):

                page_text = page.get_text()

                if page_text.strip():

                    extracted_text.append(
                        f"\n--- Page {page_number} ---\n"
                        + page_text
                    )

            document.close()

            return "\n".join(extracted_text)

        except Exception as error:

            raise RuntimeError(
                f"Could not process PDF: {error}"
            ) from error

    elif extension == ".txt":

        try:

            return file_bytes.decode("utf-8")

        except UnicodeDecodeError as error:

            raise RuntimeError(
                "The TXT file does not use UTF-8 encoding."
            ) from error

    else:

        raise ValueError(
            "Only PDF and TXT files are supported."
        )


def chunk_text(text, chunk_size=500, chunk_overlap=50):
    """
    Split text into smaller chunks with overlapping content.

    Args:
        text: Document text.
        chunk_size: Maximum approximate characters per chunk.
        chunk_overlap: Characters shared between chunks.

    Returns:
        A list of text chunks.
    """

    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError(
            "Chunk overlap must be non-negative and smaller than chunk size."
        )

    text = text.strip()

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):

        end = min(start + chunk_size, len(text))

        # Try to avoid splitting in the middle of a word.
        if end < len(text):
            boundary = text.rfind(" ", start, end)

            if boundary > start + int(chunk_size * 0.7):
                end = boundary

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        next_start = end - chunk_overlap

        # Move the starting position to the next word boundary.
        next_space = text.find(" ", next_start, end)

        if next_space != -1:
            next_start = next_space + 1

        start = next_start

    return chunks

