import gradio as gr
from horoscope_chat.main import horoscope_chat

from utils.logger import get_logger

_logs = get_logger(__name__)

#from dotenv import load_dotenv
#load_dotenv('.secrets')  # No need in app.py. Needed in main.py

chat = gr.ChatInterface(
    fn=horoscope_chat,
    type="messages"
)

if __name__ == "__main__":
    _logs.info('Starting Horoscope Chat App...')
    chat.launch()
