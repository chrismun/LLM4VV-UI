import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_nvidia_ai_endpoints import ChatNVIDIA, NVIDIAEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import torch
import os
import subprocess
import re

EMBED_URL = "http://localhost:8081/v1"
EMBEDDING_MODEL = "NV-Embed-QA"
MODEL = "mistral-nemo-12b-instruct"
CHAT_URL = "http://localhost:8000/v1/chat/completions"
MAX_RETRIES = 3

def load_spec_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

def create_vector_store_from_file(file_path):
    content = load_spec_file(file_path)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    documents = text_splitter.split_text(content)
    doc_objects = [Document(page_content=doc) for doc in documents]
    embeddings = NVIDIAEmbeddings(base_url=EMBED_URL, model=EMBEDDING_MODEL)
    return FAISS.from_documents(doc_objects, embeddings)

def retrieve_context(vector_store, query):
    return vector_store.similarity_search(query, k=3)

def generate_test_with_context(prompt, context):
    model = ChatNVIDIA(
        model=MODEL,
        base_url=CHAT_URL,
        temperature=0.7,
        max_tokens=1000,
    )
    full_prompt = f"Use the following context to create an OpenACC compiler validation test:\n\n{context}\n\nFeature: {prompt}\n\n```"
    response = model.invoke(full_prompt)
    code_snippet = response.content.split('```')[1] if '```' in response.content else ""
    return code_snippet.strip()

def compile_and_run_test(test_code):
    test_file_path = "parsedTest.c"
    with open(test_file_path, 'w', encoding='utf-8') as file:
        file.write(test_code)

    base_name = os.path.splitext(os.path.basename(test_file_path))
    build_path = os.path.join('build', base_name)

    compile_command = f"nvc -acc -Minfo=all -o {build_path} {test_file_path}"
    
    os.makedirs('build', exist_ok=True)
    
    compile_result = subprocess.run(compile_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    compile_output = compile_result.stderr.strip() if compile_result.stderr else compile_result.stdout.strip()
    
    if compile_result.returncode != 0:
        return compile_result.returncode, compile_output, ""

    run_command = f"./{build_path}"
    run_result = subprocess.run(run_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    
    run_output = run_result.stdout.strip() if run_result.stdout else run_result.stderr.strip()
    
    return run_result.returncode, compile_output, run_output

def main():
    st.title("LLM4VV")
    
    vector_store = create_vector_store_from_file("spec.txt")

    feature_prompt = st.text_input("Enter an OpenACC feature to test:")

    if feature_prompt:
        retrieved_docs = retrieve_context(vector_store, feature_prompt)
        context_texts = "\n".join([doc.page_content for doc in retrieved_docs])

        for retry in range(MAX_RETRIES + 1):
            st.write(f"Attempt {retry + 1} to generate and test code...")
            generated_code = generate_test_with_context(feature_prompt, context_texts)
            
            st.code(generated_code, language='c')

            exit_code, compiler_output, runtime_output = compile_and_run_test(generated_code)

            st.text(f"Compiler Output:\n{compiler_output}")
            st.text(f"Runtime Output:\n{runtime_output}")

            if exit_code == 0:
                st.success("Test passed.")
                break
            else:
                st.error("Test failed.")
                if retry < MAX_RETRIES:
                    st.info("Retrying with additional context based on previous outputs...")

if __name__ == "__main__":
    main()