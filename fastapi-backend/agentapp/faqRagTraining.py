from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

class InsuranceFAQVectorStore:
    def __init__(self, pdf_path: str, persist_directory: str = "sample_db"):
        self.pdf_path = pdf_path
        self.persist_directory = persist_directory

        # Initialize embeddings
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # Initialize Chroma vectorstore
        self.vectorstore = Chroma(
            collection_name="life_queries",
            embedding_function=self.embedding_model,
            persist_directory=self.persist_directory
        )

    def load_documents(self):
        """Load PDF and structure into FAQ documents with metadata."""
        loader = PyPDFLoader(self.pdf_path)
        docs = loader.load()  # list of Document objects

        structured_docs = []
        for doc in docs:
            faqs = doc.page_content.split("FAQ")
            for block in faqs:
                if block.strip():
                    faq_id_line = block.split(":")[0].strip()
                    content = block.strip()
                    structured_docs.append(
                        Document(
                            page_content=content,
                            metadata={"faq_id": faq_id_line, "category": "life-query"}
                        )
                    )
        return structured_docs

    def split_chunks(self, documents):
        """Split documents into smaller chunks."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=700,
            chunk_overlap=100,
            separators=["FAQ", "Answer", "Task", "\n\n", "\n", " "]
        )
        return text_splitter.split_documents(documents)

    def persist_to_vectorstore(self):
        """Load, chunk, and add documents to Chroma vectorstore."""
        structured_docs = self.load_documents()
        chunks = self.split_chunks(structured_docs)

        # Check if docs already exist
        existing_docs = self.vectorstore._collection.get(where={"category": "life-query"})
        if not existing_docs['ids']:
            self.vectorstore.add_documents(chunks)
            print(f"[SUCCESS] Added {len(chunks)} new chunks to vectorstore.")
        else:
            print("[INFO] Vectorstore already has documents, skipping add.")

    def debug_existing(self):
        """Print existing docs in vectorstore for debugging."""
        existing_docs = self.vectorstore._collection.get(where={"category": "life-query"})
        print(f"existing_docs: {existing_docs}")
        return existing_docs

 # Create an instance with your PDF
import os
script_dir = os.path.dirname(__file__)
pdf_path = os.path.join(script_dir, "InsuranceFaq.pdf")
faq_store = InsuranceFAQVectorStore(pdf_path)

# Step 1: Load and persist to Chroma
faq_store.persist_to_vectorstore()

# Step 2: Debug existing docs
faq_store.debug_existing()