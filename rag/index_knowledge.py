import os
import json
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

DOCS_DIR = "docs"
INDEX_PATH = "rag/faiss_index"

def build_index():
    if not os.path.exists(DOCS_DIR):
        print(f"Docs directory {DOCS_DIR} not found.")
        return

    print("Loading documents...")
    loader = DirectoryLoader(DOCS_DIR, glob="**/*.md", loader_cls=TextLoader)
    documents = loader.load()
    
    if not documents:
        print("No documents found.")
        return
        
    print(f"Loaded {len(documents)} documents. Splitting...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)
    
    print(f"Creating embeddings for {len(docs)} chunks...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local(INDEX_PATH)
    print(f"Saved FAISS index to {INDEX_PATH}")

if __name__ == "__main__":
    build_index()
