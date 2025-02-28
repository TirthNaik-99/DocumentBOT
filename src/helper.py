# Importing Important Libraries

# Fundamental Libraries
import os

# Langchain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain.vectorstores import FAISS

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate

# Miscellaneous
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import streamlit as st



load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
print(GOOGLE_API_KEY)
genai.configure(api_key=GOOGLE_API_KEY)


# Extracting text from PDFs
def get_pdf_text(pdf_docs):
    text=""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return  text


# Converting extracted data into data chunks
def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_text(text)
    return chunks


# Embedding text chunks into vector format
def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model='models/embedding-001')
    # Saving embeddings into FAISS VectorDB
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local('faiss_index')
    return vector_store


# Building the conversation chain
def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context and make sure to provide all the details.
    If the answer is not available in the provided context just say, "Answer Not Available In Given Context", DO NOT provide the wrong answer.
    Context : \n{context}?\n
    Question : \n{question}\n

    Answer : 
    """
    model = ChatGoogleGenerativeAI(model='gemini-1.5-flash', temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type='stuff', prompt=prompt)
    return chain


# Processing User Input
def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model='models/embedding-001')

    new_db = FAISS.load_local('faiss_index', embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()

    response = chain(
        {'input_documents':docs, 'question':user_question},
        return_only_outputs=True
    )

    print(response)
    st.write("Reply: ", response['output_text'])

    return response