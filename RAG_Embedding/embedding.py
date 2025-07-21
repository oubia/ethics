import os, argparse, pandas as pd
from dotenv import load_dotenv

from langchain.docstore.document   import Document
from langchain.text_splitter       import RecursiveCharacterTextSplitter
from langchain_chroma              import Chroma

from src.factory.embedding_factory import EmbeddingFactory
from src.configs.settings          import CHROMA_DIR

load_dotenv()

def build_chunks(
    docs: list[Document],                 
    target_chunk_size: int,              
    overlap: int = 80,
) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=target_chunk_size,
        chunk_overlap=overlap,
        length_function=len,
    )
    out = []
    for d in docs:
        for i, txt in enumerate(splitter.split_text(d.page_content)):
            meta = dict(d.metadata)       
            meta.update({"chunk_id": i}) 
            out.append(Document(page_content=txt, metadata=meta))
    return out


def load_csv_documents(csv_dir: str) -> list[Document]:
    docs, doc_id = [], 0
    for fn in os.listdir(csv_dir):
        if not fn.endswith(".csv"):              
            continue
        df = pd.read_csv(os.path.join(csv_dir, fn))
        for _, row in df.iterrows():
            txt = str(row.get("content", "")).strip()
            if not txt:
                continue
            docs.append(
                Document(
                    page_content=txt,
                    metadata={
                        "id":          f"doc-{doc_id}",
                        "source_file": fn,
                        "title":       os.path.splitext(fn)[0],
                    },
                )
            )
            doc_id += 1
    return docs


def store_in_chroma(
    docs: list[Document],
    collection: str,
    embedder,
):
    Chroma.from_documents(
        docs,
        embedder,
        persist_directory=CHROMA_DIR,
        collection_name=collection,
    )
    print(f"  Saved {len(docs):,} docs → collection “{collection}”")


def embed_pipeline(
    collection_root: str,        
    embedding_model: str,
    mode: str,
    csv_dir: str = "data/output_csvs/output_csvs",
):
    all_full_docs = load_csv_documents(csv_dir)
    print(f"  Loaded {len(all_full_docs):,} full documents.")

    embedder = EmbeddingFactory.get_embedding_factory(embedding_model)

    if mode in {"whole"}:
        store_in_chroma(
            docs=all_full_docs,
            collection=f"{collection_root}_full",
            embedder=embedder,
        )

    if mode in {"chunk250"}:
        chunks250 = build_chunks(all_full_docs, 250)
        store_in_chroma(
            docs=chunks250,
            collection=f"{collection_root}_native_chunk_250",
            embedder=embedder,
        )

    if mode in {"chunk750"}:
        chunks750 = build_chunks(all_full_docs, 750)
        store_in_chroma(
            docs=chunks750,
            collection=f"{collection_root}_native_chunk_750",
            embedder=embedder,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create / update Chroma collections from tourism CSVs"
    )
    parser.add_argument("--collection-name", required=True,
                        help="Root name, e.g. 'turismo'")
    parser.add_argument("--embedding-model", required=True,
                        help="Ollama or HF model name")
    parser.add_argument("--vectordb",           default="chroma",
                        help="Only 'chroma' supported")
    parser.add_argument(
        "--mode",
        choices=["whole", "chunk250", "chunk750", "all"],
        default="all",
        help="Which collection(s) to (re)build",
    )
    args = parser.parse_args()

    if args.vectordb.lower() != "chroma":
        raise ValueError("This script currently supports only ChromaDB.")

    print(
        f"  Collection root: {args.collection_name}\n"
        f"  Model:          {args.embedding_model}\n"
        f"  Mode:           {args.mode}"
    )
    embed_pipeline(
        collection_root=args.collection_name,
        embedding_model=args.embedding_model,
        mode=args.mode,
    )

    # turismo_native_chunk_750
    # turismo_native_chunk_250
    # turismo_full