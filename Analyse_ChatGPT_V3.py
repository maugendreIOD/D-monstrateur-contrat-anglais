#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
from tempfile import NamedTemporaryFile
from openai import OpenAI
import docx2txt
import PyPDF2
from PIL import Image

# Définir la clé d'API OpenAI
API_key = st.secrets["API_key"]

# Définir le mot de passe
IOD_key = st.secrets["IOD_key"]

client = OpenAI(
    api_key=API_key,
)
# Fonction d'analyse de contrat
def analyze_contract(contract_text):
    try:
        prompt = f"Perform the analysis of the contract and make a list of the key elements as well as potential risks in the contract (make sure to outline if there is no price revision clause) :\n\n{contract_text}\n"
        response = client.chat.completions.create(
            messages=[
                   {
            "role": "user",
            "content": prompt,
        }
    ],
    model="gpt-4-1106-preview",
)
        return response.choices[0].message.content
    except Exception as e:
        st.error(f'Error in analyzing contract: {e}')
        raise e

# Fonction pour interagir avec ChatGPT
def chat_with_gpt(question, contract_text):
    try:
        prompt = f"Considering the following contract: {contract_text}\n{question}"
        response =client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ],
    model="gpt-4-1106-preview",
)
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f'Error : {e}')
        raise e

# Configurer la page Streamlit
st.set_page_config(layout="wide", page_title="Analyse de Contrat avec ChatGPT", page_icon="dart", initial_sidebar_state="auto")

logo=Image.open("Logo_Iod_solutions_Horizontal_Logo.png")

st.image(logo, width=200)
st.title('Contract analysis augmented analyzer')

disclaimer = """
<span style="font-size: small;">
To use this tool or get more information, please contact contact@iod-solutions.fr
</span>
"""
st.sidebar.markdown(disclaimer, unsafe_allow_html=True)

def etat(connexion):
    st.sidebar.text(connexion)
    
st.sidebar.header("Authentification")

if 'text' not in st.session_state:
    st.session_state.text = ''

def submit():
    st.session_state.text = st.session_state.password
    st.session_state.password = ''

st.sidebar.text_input('Mot de passe', type='password', key='password', on_change=submit)
if st.session_state.text == IOD_key:
    etat("Connected")
else:
    etat("Not connected")

st.sidebar.header("Upload the file")
# Uploader le fichier:
uploaded_file = st.sidebar.file_uploader("",type=['txt', 'docx', 'pdf'], key="fileUploader")

st.sidebar.header("Choose the option")
page_options = ["Contract analysis", "Questions"]
# Use st.radio to allow selecting only one option
selected_page = st.sidebar.radio("",page_options)

if st.session_state.text == IOD_key:

    if uploaded_file is not None:
        file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}

        # Cas d'un fichier PDF
        if uploaded_file.type == 'application/pdf':
            file_path = NamedTemporaryFile(delete=False).name
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getvalue())
            pdf_file = open(file_path, 'rb')
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
            contract_text = ""
            for page in range(num_pages):
                contract_text += pdf_reader.pages[page].extract_text()

        # Cas d'un fichier txt ou docx      
        elif uploaded_file.type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            file_path = NamedTemporaryFile(delete=False).name
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getvalue())
            contract_text = docx2txt.process(file_path)
        else:
            contract_text = uploaded_file.getvalue().decode("utf-8")

        if selected_page == "Contract analysis":
            if st.button('Analyser le contrat', key="analyzeButton"):
                result = analyze_contract(contract_text)
                st.text_area("Analysis outcome", value=result, height=500, key="resultTextArea")

        elif selected_page == "Questions":
            user_question = st.text_input("Ask your question", "")
            if user_question:
                answer = chat_with_gpt(user_question, contract_text)
                st.write(f"Réponse : {answer}")
        
