import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from agent.tools import coding_tools

load_dotenv()


llm = ChatGoogleGenerativeAI(
    model=os.getenv('GEMINI_MODEL'),
    google_api_key=os.getenv('GEMINI_API_KEY')
)

llm_with_tools = llm.bind_tools(coding_tools)