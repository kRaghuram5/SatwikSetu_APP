import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_community.document_loaders import WebBaseLoader


ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(ENV_PATH)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
if not OPENAI_BASE_URL:
    raise ValueError("OPENAI_BASE_URL is not set in the environment variables.")
if not OPENAI_MODEL:
    raise ValueError("OPENAI_MODEL is not set in the environment variables.")

client = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
    model=OPENAI_MODEL,
    temperature=0.7
)

# prompt_template = PromptTemplate(
#     input_variables=["topic"],
#     template="Explain what is {topic} and how to prevent it. Limit it to 100 characters."
# )

# response = client.invoke(
#     prompt_template.format_prompt(topic ="Tomato late blight")
# )

# print(response.content)

# chat_prompt = ChatPromptTemplate.from_messages([
#     ("system", "You are a Agricultural advisor. Be concise and accurate."),
#     ("human", "Explain what is {topic} and how to prevent it. Limit it to {num_words} characters.")
# ])

# messages = chat_prompt.invoke({"topic":"Tomato Late Blight","num_words":100})
# response = client.invoke(messages)
# print(response.content)

# context
# context = """Tomato Late Blight is caused by Phytophthora infestans. It produces dark, water-soaked lesions on leaves and stems. The disease spreads rapidly in cool, moist conditions. Treatment includes copper-based fungicide (Bordeaux mixture) or Mancozeb at first signs. Organic option: neem oil spray every 7 days."""

# rag_prompt = ChatPromptTemplate.from_messages([
#     ("system", "You are a Agricultural advisor. Answer using only the provided context"),
#     ("human", """Context: 
#     {context}
    
#     Question: {question}
#     Answer: """)
# ])

# messages = rag_prompt.invoke({"context": context, "question": "How to treat Tomato disease?"})
# response = client.invoke(messages)
# print(response.content)

WIKI_URL = "https://en.wikipedia.org/wiki/Phytophthora_infestans"
loader = WebBaseLoader(WIKI_URL)
docs = loader.load()
web_context = docs[0].page_content[:6000]

rag_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a Agricultural advisor. Answer using only the provided context"),
    ("human", """Context (from {source}):
    {web_context}
     
    Question: {question}
    Answer: """)
])

messages = rag_prompt.invoke({
    "source": WIKI_URL,
    "web_context": web_context,
    "question": "what is Phytophthora infestans and how can farmers manage late blight?"})
response = client.invoke(messages)
print(response.content)

