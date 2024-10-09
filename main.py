import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_nvidia_ai_endpoints import ChatNVIDIA, NVIDIAEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import torch
import os
import subprocess

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

def generate_test_with_context(prompt, context, previous_code=None, previous_output=None):
    model = ChatNVIDIA(
        model=MODEL,
        base_url=CHAT_URL,
        temperature=0.7,
        max_tokens=1000,
    )
    
    full_prompt = (
        f"Use the following context from the specification to create an OpenACC compiler validation test in C. "
        f"Return 0 if the feature works, 1 otherwise.\n\n"
        f"Context:\n{context}\n\n"
        f"Feature: {prompt}\n\n"
    )
    
    if previous_code:
        full_prompt += f"Previous Code Attempt:\n{previous_code}\n\n"
    
    if previous_output:
        full_prompt += f"Previous Compiler Output:\n{previous_output}\n\n"

    full_prompt += "```"

    response = model.invoke(full_prompt)
    code_snippet = response.content.split('```')[1] if '```' in response.content else ""
    return code_snippet.strip()

def compile_and_run_test(test_code):
    test_file_path = "parsedTest.c"
    with open(test_file_path, 'w', encoding='utf-8') as file:
        file.write(test_code)

    base_name = os.path.splitext(os.path.basename(test_file_path))[0]
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

def evaluate_test_with_llmj(feature_prompt, context_texts, generated_code, compiler_output, runtime_output):
    llmj_prompt = (
        f"Evaluate the following test for the feature '{feature_prompt}'.\n\n"
        f"Context:\n{context_texts}\n\n"
        f"Generated Code:\n{generated_code}\n\n"
        f"Compiler Output:\n{compiler_output}\n\n"
        f"Runtime Output:\n{runtime_output}\n\n"
        f"Is this a good test? Provide a one-sentence evaluation."
    )
    
    model = ChatNVIDIA(
        model=MODEL,
        base_url=CHAT_URL,
        temperature=0.5,
        max_tokens=100,
    )
    
    response = model.invoke(llmj_prompt)
    
    return response.content.strip()

def main():
    st.title("LLM4VV")
    
    vector_store = create_vector_store_from_file("spec.txt")

    feature_prompt = st.text_input("Enter an OpenACC feature to test:")

    if feature_prompt:
        retrieved_docs = retrieve_context(vector_store, feature_prompt)
        context_texts = "\n".join([doc.page_content for doc in retrieved_docs])

        with st.expander("Retrieved Context from Spec", expanded=False):
            st.text(context_texts)

        previous_code = None
        previous_output = None

        for retry in range(MAX_RETRIES + 1):
            st.write(f"Attempt {retry + 1} to generate and run test...")
            generated_code = generate_test_with_context(feature_prompt, context_texts, previous_code, previous_output)

            if generated_code.startswith("c\n"):
                generated_code = generated_code[2:]

            with st.expander("Generated Test", expanded=False):
                st.code(generated_code, language='c')

            exit_code, compiler_output, runtime_output = compile_and_run_test(generated_code)

            with st.expander("Compiler Output", expanded=False):
                st.text(compiler_output)
            
            with st.expander("Runtime Output", expanded=False):
                st.text(runtime_output)

            # Evaluate the test with LLMJ after each attempt
            evaluation_result = evaluate_test_with_llmj(feature_prompt, context_texts, generated_code, compiler_output, runtime_output)
            
            with st.expander("LLM Evaluation", expanded=False):
                st.text(evaluation_result)

            if exit_code == 0:
                st.success("Test passed.")
                break
            else:
                st.error("Test failed.")
                if retry < MAX_RETRIES:
                    st.info("Retrying with additional context based on previous outputs...")

            previous_code = generated_code
            previous_output = compiler_output

if __name__ == "__main__":
    main()