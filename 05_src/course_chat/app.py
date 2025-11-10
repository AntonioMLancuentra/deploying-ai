# Run set PYTHONIOENCODING=utf-8 && python -m course_chat.app

from course_chat.main import get_graph
from langchain_core.messages import HumanMessage, AIMessage
import gradio as gr

from utils.logger import get_logger

_logs = get_logger(__name__)

llm = get_graph()

#from dotenv import load_dotenv
#load_dotenv('.secrets')  # No need in app.py. Needed in main.py

# To avoid warnings during execution, it works here, not at the top of imports. I installed last versions of uvicorn, gradio, websockets. 
# These warnings are from third-party code. The maintainers of uvicorn and gradio need to update their code to use the newer websockets API.
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="websockets")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="uvicorn")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="gradio")
# warnings.filterwarnings("ignore", category=DeprecationWarning)

def course_chat(message: str, history: list[dict]) -> str:
    langchain_messages = []
    n = 0
    _logs.debug(f"History: {history}")
    for msg in history:
        if msg['role'] == 'user':
            langchain_messages.append(HumanMessage(content=msg['content']))
        elif msg['role'] == 'assistant':
            langchain_messages.append(AIMessage(content=msg['content']))
            n += 1
    langchain_messages.append(HumanMessage(content=message))

    state = {
        "messages": langchain_messages,
        "llm_calls": n
    }

    response = llm.invoke(state)
    return response['messages'][len(response['messages']) - 1].content

chat = gr.ChatInterface(
    fn=course_chat,
    type="messages"
)

if __name__ == "__main__":
    _logs.info('Starting Course Chat App...')
    chat.launch()
