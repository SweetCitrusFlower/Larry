from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_core.documents import Document
from typing import List

def chunk_markdown(markdown_text: str) -> List[Document]:
    """
    Splits the extracted Markdown based on semantic headers.
    """
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    # This automatically retains the headers in the Document metadata
    md_header_splits = markdown_splitter.split_text(markdown_text)
    
    return md_header_splits
