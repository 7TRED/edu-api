from langchain.chains import RetrievalQA
from langchain.vectorstores.redis import Redis
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import AzureOpenAI
import os
import logging
from PyPDF2 import PdfFileReader, PdfFileWriter
from dotenv import load_dotenv

load_dotenv()

openai_api_base = os.environ.get("OPENAI_API_BASE")
openai_api_key = os.environ.get("OPENAI_API_KEY")
openai_api_version = os.environ.get("OPENAI_API_VERSION")
openai_api_type = os.environ.get("OPENAI_API_TYPE")


llm = AzureOpenAI(

    deployment_name="text-davinci-003",

    model_name="text-davinci-003",
    openai_api_base=openai_api_base,
    openai_api_key=openai_api_key,
    openai_api_type=openai_api_type,
    openai_api_version=openai_api_version

)

embeddings = OpenAIEmbeddings(

    deployment="text-embedding-ada-002",

    model="text-embedding-ada-002",
    openai_api_base=openai_api_base,
    openai_api_key=openai_api_key,
    openai_api_type=openai_api_type,
    openai_api_version=openai_api_version
)

# Load PDF File


def loadPDFAndSaveLocallyTemp(file, filename):
    base_dir = os.getcwd()
    dir = "files"
    if (not os.path.exists(os.path.join(base_dir, dir))):
        os.mkdir(os.path.join(base_dir, dir))

    out_file_path = os.path.join(base_dir, dir, filename)

    pdf_writer = PdfFileWriter()
    pdf_reader = PdfFileReader(file.stream)

    for page in range(pdf_reader.getNumPages()):
        # Add each page to the writer object
        pdf_writer.addPage(pdf_reader.getPage(page))

    with open(out_file_path, "wb") as out:
        pdf_writer.write(out)

    return out_file_path


def loadPDFLangChain(filepath):
    loader = PyPDFLoader(filepath)
    return loader.load_and_split()


def generateEmbeddingsAndStore(pages):
    try:
        rds = Redis.from_documents(
            pages, embeddings, redis_url="redis://localhost:6379",  index_name='link')
        return True
    except Exception:
        logging.info("Failed to store or generate embeddings")
        return False


# loader = PyPDFLoader("C:/Users/shvishno/Downloads/lefl101.pdf")

# pages = loader.load_and_split()


# # Create Embeddings


# rds = Redis.from_documents(
#     pages, embeddings, redis_url="redis://localhost:6379",  index_name='link')


# Create QA


def answerQuery(query, collection_name="test"):
    from langchain.vectorstores.pgvector import PGVector

    CONNECTION_STRING = PGVector.connection_string_from_db_params(

        driver=os.environ.get("PGVECTOR_DRIVER"),

        host=os.environ.get("PGVECTOR_HOST"),

        port=int(os.environ.get("PGVECTOR_PORT")),

        database=os.environ.get("PGVECTOR_DATABASE"),

        user=os.environ.get("PGVECTOR_USER"),

        password=os.environ.get("PGVECTOR_PASSWORD"),

    )

    db = PGVector(

        collection_name=collection_name,

        connection_string=CONNECTION_STRING,

        embedding_function=embeddings,

    )

    from langchain.chains import RetrievalQA

    qa = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=db.as_retriever())

    return qa.run(query)


# test
if __name__ == "__main__":
    # pages = loadPDFLangChain(
    # "C:\\Users\\singhmani\\Downloads\\CrossTenant_MMS_Design.pdf")

    # generateEmbeddingsAndStore(pages)

    # print(answerQuery(
    # "Can you tell me some questions related to this chapter"))

    print(answerQuery(
        "I am a teacher, preparin a question set from this chapter. Can you output five questions related to this chapter."))
