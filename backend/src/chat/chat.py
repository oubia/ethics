import json
from src.moderation.llamaguard import run_llamaguard
from src.rag_models.retriever.retriever_factory import Retrieval_Factory
from src.rag_models.vectorestore.vectorstore_factory import VectorStoreFactory
from src.utils.prompts.prompt import general_prompt
import logging

logger = logging.getLogger(__name__)


class Chat:

    def __init__(
        self,
        model,
        vectorstore_type: str,
        collection_name: str,
        embedding_model_name: str,
        chunk_size: int,
        retriever_type: str,
        max_retrievals: int = 10,
    ):
        self.model = model
        self.prompt = general_prompt

        self.vectorstore = VectorStoreFactory(
            vectorstore_type,
            collection_name,
            embedding_model_name,
        ).get_vectorstore()
        self.max_retrievals = max_retrievals
        self.retriever_type = retriever_type
        self.chunk_size = chunk_size

    async def ask_stream(self, query: str):
        logger.info("Received query: %s", query)

        # # Input moderation
        # try:
        #     verdict_in = run_llamaguard(query, role="user")
        #     logger.info("Input moderation verdict: %s", verdict_in)

        #     if not verdict_in.get("allowed", False):
        #         blocked = {
        #             "type": "Input moderation error",
        #             "data": f"Messaggio non consentito in query: {', '.join(verdict_in.get('categories', []))}"
        #         }
        #         logger.warning("Blocking input: %s", blocked['data'])
        #         yield blocked
        #         return

        # except Exception as e:
        #     logger.error("Input moderation failed: %s", e, exc_info=True)
        #     yield {"error": f"Moderation input check failed: {str(e)}"}
        #     return

        # Normal RAG pipeline
        try:
            logger.info("Passing into retrieval handler")
            retrieval_handler = Retrieval_Factory(
                llm=self.model,
                vectorstore=self.vectorstore,
                chunk_size=self.chunk_size,
                max_retrievals=self.max_retrievals,
            )
            logger.info("Handler created successfully")

            retriever_methods = {
                "Similarity-research": retrieval_handler.answer_with_similarity,
                "Contextual-Compression": retrieval_handler.answer_with_compression,
                "Answer-With-Multiquery": retrieval_handler.answer_with_multiquery,
                "Hybrid-fusion": retrieval_handler.answer_with_hybrid,
            }
            method = retriever_methods.get(
                self.retriever_type, retrieval_handler.answer_with_similarity
            )
            logger.info("Retrieved method %s", self.retriever_type)

            # Collect full response while streaming
            answer_text = ""
            async for payload in method(query, prompt_template=self.prompt):
                logger.debug("Streaming payload: %s", str(payload)[:100])
                yield payload

                # try to extract textual content from payload if it's JSON
                chunk_text = ""

                if isinstance(payload, str):
                    try:
                        data = json.loads(payload)
                        if isinstance(data, dict):
                            chunk_text = data.get("answer", "")
                        elif isinstance(data, str):
                            # raw string, not JSON dict
                            chunk_text = ""
                    except Exception:
                        chunk_text = ""

                elif isinstance(payload, dict):
                    chunk_text = payload.get("answer", "")

                answer_text += chunk_text

            logger.info("Finished streaming RAG output. Full answer length: %d", len(answer_text))

        except Exception as error:
            logger.error("Backend crashed: %s", error, exc_info=True)
            yield {"error": f"Error processing request: {error}"}
            return

        # # Output moderation
        # try:
        #     verdict_out = run_llamaguard(answer_text, role="assistant")
        #     logger.info("Output moderation verdict: %s", verdict_out)

        #     if not verdict_out.get("allowed", False):
        #         blocked = {
        #             "type": "Output moderation error",
        #             "data": f"Risposta non consentita in output: {', '.join(verdict_out.get('categories', []))}"
        #         }
        #         logger.warning("Blocking unsafe output: %s", blocked['data'])
        #         yield blocked
        #         return
        #     else:
        #         yield answer_text

        except Exception as e:
            logger.error("Output moderation failed: %s", e, exc_info=True)
            yield {"error": f"Moderation output check failed: {str(e)}"}
            return