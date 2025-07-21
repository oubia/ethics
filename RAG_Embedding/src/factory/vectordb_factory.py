class VectorStoreFactory:
    def __init__(self, chroma_persist_dir = None):
        
        self.chroma_persist_dir = chroma_persist_dir

    def get_vectorstore(self, vectorstore_type: str, collection_name: str, embedding_model):

        if vectorstore_type.lower() == "chroma":
            print("Using Chroma db (direct client approach)")
            import chromadb
            if not self.chroma_persist_dir:
                raise ValueError("Chroma persist directory must be provided for Chroma vector store.")
            
            client = chromadb.PersistentClient(path=self.chroma_persist_dir)
            try:
                collection = client.get_collection(name=collection_name)
                print(f"Collection '{collection_name}' found in Chroma.")
            except Exception as e:
                print(f"Collection '{collection_name}' not found, creating a new one. Error: {e}")
                collection = client.create_collection(name=collection_name)
            return collection

        else:
            raise Exception(f"Unsupported vector store type: '{vectorstore_type}'")