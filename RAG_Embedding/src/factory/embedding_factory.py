class EmbeddingFactory:
    @staticmethod
    def get_embedding_factory(embedding_model: str):
        if embedding_model.startswith("nomic-embed-text"):
            from src.configs.settings import OLLAMA_EMBEDDINGS_ENDPOINT
            
            from langchain_community.embeddings import OllamaEmbeddings

            embeddings = OllamaEmbeddings(model=embedding_model, show_progress=True, base_url=OLLAMA_EMBEDDINGS_ENDPOINT)
            return embeddings
        
        else:
            raise Exception(f"No embedding model found for '{embedding_model}'")

