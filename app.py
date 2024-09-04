import os
import subprocess

import streamlit as st

from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain.memory import ConversationBufferWindowMemory

st.set_page_config(layout="wide", page_title="App3 Generator")

DEFAULT_SERVICE_URL = os.getenv("INFERENCE_SERVER_URL")
DEFAULT_MODEL_NAME = os.getenv("MODEL_NAME")

CUSTOM_SERVICE_URL = "http://localhost:8080/v1"
CUSTOM_MODEL_NAME = "llama-3-8b-chat"

OPTION_SERVICE_URL_DEFAULT = "Use default service"
OPTION_SERVICE_URL_CUSTOM = "Use custom service"
REQUEST_TIMEOUT = 600
DOCUMENT_SOURCE_DIRECTORY = "source_documents"

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are world class technical advisor. Keep your answers brief, less than 50 words."),
    MessagesPlaceholder(variable_name="history"),
    ("user", "{input}")
])

service_url = ""
model_name = ""

def write_message(user, message):
    with st.chat_message(user):
        st.markdown(message)


if "messages" not in st.session_state:
    st.session_state.messages = []

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False

@st.cache_resource()
def memory():
    memory = ConversationBufferWindowMemory(return_messages=True,k=3)
    return memory

with st.sidebar:
    st.image("assets/logo.svg")
    st.subheader("", divider="grey")
    st.write("")

    service_option = st.radio(
        "Select chat service:", [OPTION_SERVICE_URL_DEFAULT, OPTION_SERVICE_URL_CUSTOM]
    )

    if service_option == OPTION_SERVICE_URL_DEFAULT:
        service_url = DEFAULT_SERVICE_URL
        model_name = DEFAULT_MODEL_NAME

    # base-input
    elif service_option == OPTION_SERVICE_URL_CUSTOM:
        service_url = st.text_input(
            "Input service URL:",
            value=CUSTOM_SERVICE_URL,
            help=CUSTOM_SERVICE_URL,
        )
        model_name = CUSTOM_MODEL_NAME

    else:
        raise ValueError("Unsupported service option!")

    if st.button("Connect"):
        if "chat" not in st.session_state:
            st.session_state.chat = ChatOpenAI(base_url=service_url,
                                               api_key="sk-no-key-required",
                                               model=model_name,
                                               streaming=True,
                                               callbacks=[StreamlitCallbackHandler(st.empty(),
                                                                                   expand_new_thoughts=True,
                                                                                   collapse_completed_thoughts=True)])
            st.session_state.chain = LLMChain(llm=st.session_state.chat,
                prompt=prompt,
                verbose=False,
                memory=memory())

            st.session_state.start_chat = True

if st.session_state.start_chat:
    st.title("💬 App3 Generator")
    st.caption("🚀 A LLM app driven by LlamaEdge")

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

    with st.spinner("Loading documents..."):
        uploaded_files = st.file_uploader(
            "Upload your documents",
            type=("txt", "md", "pdf"),
            accept_multiple_files=True,
        )
        if uploaded_files and len(uploaded_files) > 0:
            num_files = len(st.session_state.uploaded_files)
            for f in uploaded_files:
                if not os.path.exists(DOCUMENT_SOURCE_DIRECTORY):
                    os.makedirs(DOCUMENT_SOURCE_DIRECTORY)
                file_path = os.path.join(DOCUMENT_SOURCE_DIRECTORY, f.name)
                if file_path not in st.session_state.uploaded_files:
                    print(f"[INFO] Saving {f.name}")
                    st.session_state.uploaded_files.append(file_path)
                    with open(
                        os.path.join(DOCUMENT_SOURCE_DIRECTORY, f.name), "wb"
                    ) as out_file:
                        out_file.write(f.read())

            for f in uploaded_files:
                file_path = os.path.join(DOCUMENT_SOURCE_DIRECTORY, f.name)
                cmd = "java -jar tika-app-3.0.0-BETA2.jar --text '" + file_path + "' | jbang run fabric.java -p create_app3 -s"
                #print(os.popen(cmd).read())
                print(f"[INFO] Processing {f.name}")
                my_env = os.environ.copy()
                my_env["INFERENCE_SERVER_URL"] = service_url
                my_env["MODEL_NAME"] = model_name
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=my_env)
                with st.chat_message("assistant"):
                    while process.poll() is None:
                        nextline = process.stdout.readline()
                        if nextline == '':
                            continue
                        st.markdown(nextline.decode())
