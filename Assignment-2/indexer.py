import os
from pathlib import Path

from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

PAPERS_DIR = Path("papers")
FAISS_DIR = Path("faiss_index")

# Extract text from all PDFs, keeping track of source and page
documents = []
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

for pdf_file in sorted(PAPERS_DIR.glob("*.pdf")):
    reader = PdfReader(pdf_file)
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if not text:
            continue
        chunks = splitter.split_text(text)
        for chunk in chunks:
            documents.append({
                "text": chunk,
                "metadata": {"source": pdf_file.name, "page": page_num},
            })

print(f"Created {len(documents)} chunks from {len(list(PAPERS_DIR.glob('*.pdf')))} PDFs")

# Embed and store in FAISS
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
vectorstore = FAISS.from_texts(
    texts=[d["text"] for d in documents],
    embedding=embeddings,
    metadatas=[d["metadata"] for d in documents],
)
vectorstore.save_local(str(FAISS_DIR))
print(f"FAISS index saved to {FAISS_DIR}")
