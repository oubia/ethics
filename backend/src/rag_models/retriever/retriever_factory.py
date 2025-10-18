import asyncio
from typing import AsyncGenerator
from typing import List 
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.retrievers import (
    ContextualCompressionRetriever,
    EnsembleRetriever,
    BM25Retriever,
)
from langchain_core.retrievers import BaseRetriever 
from langchain_community.document_compressors.rankllm_rerank import RankLLMRerank
from langchain.schema import HumanMessage, AIMessage, Document
from langchain.prompts import ChatPromptTemplate

class Retrieval_Factory:

    def __init__(self, llm, vectorstore, chat_history: list | None = None, chunk_size: int = 750, max_retrievals: int = 10):
        self.llm = llm
        self.vectorstore = vectorstore
        self.chunk_size = chunk_size
        self.chat_history = chat_history or []
        self.max_retrievals = max_retrievals

    def load_raw_documents(self,csv_dir="D:\homy\S9\data-text-mining\RAG_Embeddings\data\output_csvs\output_csvs"):
        import os, pandas as pd
        from langchain.schema import Document

        docs = []
        for filename in os.listdir(csv_dir):
            if filename.endswith(".csv"):
                df = pd.read_csv(os.path.join(csv_dir, filename))
                for idx, row in df.iterrows():
                    txt = row.get("content", "").strip()
                    if txt:
                        docs.append(
                            Document(
                                page_content=txt,
                                metadata={
                                    "source_file": filename,
                                    "title": os.path.splitext(filename)[0],
                                },
                            )
                        )
        return docs

    def format_chat_history(self, chat_history):
        messages = []
        for item in chat_history:
            role, content = item["role"], item["content"].strip()
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
        return messages

    #  1) Standard vector-similarity (or MMR) retriever
  
    def build_similarity_retriever(self,  mmr: bool = False):
        if mmr:
            return self.vectorstore.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 10, "lambda_mult": 0.5}
            )

            
        return self.vectorstore.as_retriever(
            #search_type="similarity", search_kwargs={"k": 10},
            search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.5, "k": 10}
        )

    def build_compression_retriever(self):

        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain.retrievers.document_compressors import (
            DocumentCompressorPipeline,
            EmbeddingsFilter, 
        )
        from langchain_community.document_transformers import EmbeddingsRedundantFilter

        from langchain.retrievers import ContextualCompressionRetriever
        from langchain.retrievers.document_compressors import LLMChainExtractor

        try:
            from langchain.retrievers.document_compressors.base import BaseDocumentCompressor
            from typing import List
            from pydantic import BaseModel

            class TopNSliceCompressor(BaseDocumentCompressor, BaseModel):
                top_n: int = 10

                model_config = {"arbitrary_types_allowed": True}

                def compress_documents(
                    self,
                    documents: List[Document],
                    *args,             
                    query: str | None = None,
                    **kwargs,             
                ) -> List[Document]:
                    return documents[: self.top_n]

            slice_filter = TopNSliceCompressor(top_n=10)

            splitter = RecursiveCharacterTextSplitter(
                chunk_size    = int(self.chunk_size) ,
                chunk_overlap = int(self.chunk_size * 0.1)   
            )   

            compressor = DocumentCompressorPipeline(transformers=[splitter, slice_filter] )


            return ContextualCompressionRetriever(
                base_compressor = compressor,
                base_retriever  = self.vectorstore.as_retriever(
                    search_type   = "similarity",
                    search_kwargs = {"k":10},
                ),
            )   
        except Exception as err:
            import logging, traceback
            logging.error("Failed to build ContextualCompressionRetriever")
            logging.error("".join(traceback.format_exception(err)))
            raise RuntimeError(f"Failed to build compression retriever: {err}") from err

    def build_multiquery_retriever(
        self,
        n_queries: int = 4,         
        top_k    : int = 10,           
    ) -> "MultiQueryRetriever":

        from langchain.retrievers.multi_query import MultiQueryRetriever

        base = self.vectorstore.as_retriever(
            search_type   = "similarity",
            search_kwargs = {"k": top_k},
        )
        from langchain.prompts import PromptTemplate

        prompt = PromptTemplate.from_template(
        "You are a search expert. Generate {n} diverse, \
        semantically different search queries that could be used to look up \
        answers to the user question.\n\nUser question: {question}"
    ).partial(n=n_queries)
        mqr = MultiQueryRetriever.from_llm(
            retriever   = base,
            llm         = self.llm,
            prompt         = prompt,     
            include_original = True,     
            
        )
        return SliceRetriever(base_retriever=mqr, k=self.max_retrievals)
        #return mqr


            
    from langchain.retrievers import BM25Retriever, EnsembleRetriever

    def build_hybrid_fusion_retriever(self,sparse_k: int = 20,alpha: float = 0.5):
        """
        alpha = 1   → only dense scores
        alpha = 0   → only BM25 scores
        """
        from langchain.schema import Document
        from langchain.retrievers import BM25Retriever, EnsembleRetriever

        dense = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 10},
        )

        try:
            results = self.vectorstore.get(
                include=["documents", "metadatas"],
                limit=10,         
            ) or {}
            print(len(results), "results found in vectorstore")
            docs_list  = results.get("documents") or []
            metas_list = results.get("metadatas") or []

            if not docs_list or not metas_list:
                raise RuntimeError(
                    f"No documents found in vectorstore (docs={len(docs_list)}, metas={len(metas_list)})"
                )

            all_docs = [
                Document(page_content=text, metadata=meta)
                for text, meta in zip(docs_list, metas_list)
            ]
            bm25 = BM25Retriever.from_documents(all_docs)
            bm25.k = sparse_k

            hybrid = EnsembleRetriever(
                retrievers=[dense, bm25],
                weights=[alpha, 1 - alpha],
            )
            #return hybrid
            return SliceRetriever(base_retriever=hybrid, k=self.max_retrievals)


        except Exception as err:
            import logging, traceback
            logging.error("Failed to build Hybrid-Fusion retriever")
            logging.error("".join(traceback.format_exception(err)))
            raise RuntimeError(f"Failed to build hybrid retriever: {err}") from err

    #  Generic ConversationalRetrieval chain
    async def converse(
        self,
        query: str,
        prompt_template: str,
        retriever,
    ) -> AsyncGenerator[str, None]:
        from langchain.memory import ConversationBufferMemory
        from langchain.chains import ConversationalRetrievalChain
        import numpy as np

        memory = ConversationBufferMemory(
            memory_key="chat_history", output_key="answer"
        )
        prompt = ChatPromptTemplate.from_template(prompt_template)

        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=memory,
            combine_docs_chain_kwargs={"prompt": prompt},
            return_source_documents=True,
            verbose=True,
        )

        response = await qa_chain.ainvoke(query)
        answer = response.get("answer", "")
        source_docs = response.get("source_documents", [])


        # Calculate confidence scores
        confidence_info = self.calculate_confidence_scores(query, answer, source_docs)
        yield {"type": "confidence", "data": confidence_info}

        source_files = []
        for doc in source_docs:
            src_file = doc.metadata.get("source_file")
            if src_file and src_file not in source_files:
                source_files.append(src_file)

        for ch in answer:
            yield {"type": "chunk", "data": ch}
            await asyncio.sleep(0.01)

        yield {"type": "sources", "data": source_files}

    def calculate_confidence_scores(self, query: str, answer: str, source_docs: List[Document]) -> dict:
        """Calculate confidence scores for the RAG response"""
        print(f"CONFIDENCE: Starting calculation with {len(source_docs) if source_docs else 0} documents")
        print(f"CONFIDENCE: Query: {query[:50]}...")
        print(f"CONFIDENCE: Answer length: {len(answer) if answer else 0} characters")
        import numpy as np
        
        if not source_docs or not answer:
            return {
                "confidence_score": 0.0,
                "confidence_level": "Low",
                "confidence_color": "red",
                "details": {
                    "num_sources": 0,
                    "answer_length": len(answer.split()) if answer else 0,
                    "query_complexity": len(query.split())
                }
            }
        
        # Factor 1: Number of supporting documents (0-1 scale)
        doc_count_score = min(len(source_docs) / 5, 1.0)  # 5+ docs = max score
        
        # Factor 2: Average document length (proxy for detail)
        avg_doc_length = sum(len(doc.page_content.split()) for doc in source_docs) / len(source_docs)
        doc_quality_score = min(avg_doc_length / 100, 1.0)  # 100+ words = max score
        
        # Factor 3: Answer completeness relative to query
        query_words = len(query.split())
        answer_words = len(answer.split())
        completeness_score = min(answer_words / (query_words * 5), 1.0)  # 5:1 ratio = max
        
        # Factor 4: Source diversity (different source files)
        unique_sources = set()
        for doc in source_docs:
            source = doc.metadata.get("source_file", "unknown")
            unique_sources.add(source)
        diversity_score = min(len(unique_sources) / 3, 1.0)  # 3+ different sources = max
        
        # Calculate weighted confidence
        confidence_score = (
            doc_count_score * 0.3 +      # 30% - number of sources
            doc_quality_score * 0.2 +     # 20% - source quality
            completeness_score * 0.3 +    # 30% - answer completeness
            diversity_score * 0.2         # 20% - source diversity
        )
        
        # Determine confidence level and color
        if confidence_score >= 0.75:
            confidence_level = "High"
            confidence_color = "green"
        elif confidence_score >= 0.5:
            confidence_level = "Medium"
            confidence_color = "orange"
        else:
            confidence_level = "Low"
            confidence_color = "red"
        
        return {
            "confidence_score": round(confidence_score, 2),
            "confidence_level": confidence_level,
            "confidence_color": confidence_color,
            "details": {
                "num_sources": len(source_docs),
                "unique_sources": len(unique_sources),
                "avg_doc_length": round(avg_doc_length),
                "answer_length": answer_words,
                "query_complexity": query_words,
                "factors": {
                    "doc_count": round(doc_count_score, 2),
                    "doc_quality": round(doc_quality_score, 2),
                    "completeness": round(completeness_score, 2),
                    "diversity": round(diversity_score, 2)
                }
            }
        }
    
    # def get_relevant_docs(self, query):
    #     return self.vectorstore.similarity_search(query, k=self.max_retrievals)

    async def answer_with_similarity(
        self, query: str, prompt_template: str, mmr=False
    ):
        print(f"this is the similarity retriever")
        retriever = self.build_similarity_retriever(mmr=mmr)
        async for chunk in self.converse(query, prompt_template, retriever):
            yield chunk

    async def answer_with_compression(
        self, query: str, prompt_template: str
    ):
        print(f"this is the compression retriever")
        retriever = self.build_compression_retriever()

        async for chunk in self.converse(query, prompt_template, retriever):
            yield chunk

    async def answer_with_multiquery(
            self,
            query: str,
            prompt_template: str,
            n_queries: int = 4,
            top_k: int = 10,
    ):
        retriever = self.build_multiquery_retriever(
            n_queries=n_queries,
            top_k=top_k,
        )
        async for chunk in self.converse(query, prompt_template, retriever):
            yield chunk


    async def answer_with_hybrid(
        self,
        query: str,
        prompt_template: str,
    ):
        print(f"this is the answer_with_hybrid retriever")
        dense_k = 10
        sparse_k = 20
        alpha = 0.5
        retriever = self.build_hybrid_fusion_retriever(
            sparse_k=sparse_k, alpha=alpha
        )
        async for chunk in self.converse(query, prompt_template, retriever):
            yield chunk




class SliceRetriever(BaseRetriever):
    """Wrap any retriever and return only the first *k* docs."""
    base_retriever: BaseRetriever
    k: int = 10

    # ---- sync ----
    def _get_relevant_documents(
        self, query: str, *, run_manager=None, **kwargs
    ) -> List[Document]:
        docs = self.base_retriever._get_relevant_documents(
            query, run_manager=run_manager, **kwargs  # type: ignore
        )
        return docs[: self.k]

    # ---- async ----
    async def _aget_relevant_documents(
        self, query: str, *, run_manager=None, **kwargs
    ) -> List[Document]:
        docs = await self.base_retriever._aget_relevant_documents(
            query, run_manager=run_manager, **kwargs  # type: ignore
        )
        return docs[: self.k]