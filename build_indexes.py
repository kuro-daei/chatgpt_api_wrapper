import os
import logging
from llama_index import (
    GPTSimpleVectorIndex,
    LLMPredictor,
    OpenAIEmbedding,
    ServiceContext,
    Document,
)
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from config import config, configure_logging

configure_logging(config())

load_dotenv()

MD_FOLDER = "data/src_mds"
INDEX_FLODER = "data/indexes"

llm_predictor = LLMPredictor(
    llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", max_input_size=4096)
)
embed_model = OpenAIEmbedding(model="text-embedding-ada-002")
service_context = ServiceContext.from_defaults(
    llm_predictor=llm_predictor, embed_model=embed_model
)


def buid_index(md_folder_path):
    index_name = os.path.basename(md_folder_path)
    index_path = os.path.join(INDEX_FLODER, f"{index_name}.json")
    logging.info("md folder: %s", md_folder_path)
    logging.info("index: %s", index_path)

    documents = []
    for root, _, files in os.walk(md_folder_path):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                logging.info("file_path: %s", file_path)
                with open(file_path, "r", encoding="utf-8") as filehandler:
                    content = filehandler.read()
                documents.append(Document(content))

    index = GPTSimpleVectorIndex.from_documents(
        documents, service_context=service_context
    )
    index.save_to_disk(index_path)


if __name__ == "__main__":
    for md_folder_name in os.listdir(MD_FOLDER):
        folder_path = os.path.join(MD_FOLDER, md_folder_name)
        if os.path.isdir(folder_path):
            buid_index(folder_path)
