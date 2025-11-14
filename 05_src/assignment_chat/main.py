from langgraph.graph import StateGraph, MessagesState, START
from langchain.chat_models import init_chat_model
from langgraph.prebuilt.tool_node import ToolNode, tools_condition
from langchain_core.messages import SystemMessage

from dotenv import load_dotenv

from assignment_chat.prompts import return_instructions
from assignment_chat.tools_rag import rag
from utils.logger import get_logger


_logs = get_logger(__name__)
load_dotenv(".secrets") # relative path from where the code is executed, not from where this file is

import os
os.environ["LANGSMITH_TRACING"] = "false"   # otherwise LANGSMITH_TRACING=true ihn .env messes up

chat_agent = init_chat_model(
    "openai:gpt-4o-mini",
    #api_key = os.getenv("OPENAI_API_KEY"),
)
tools = [rag]

instructions = return_instructions()



# @traceable(run_type="llm")
def call_model(state: MessagesState):
    """LLM decides whether to call a tool or not"""
    response = chat_agent.bind_tools(tools).invoke( [SystemMessage(content=instructions)] + state["messages"])
    return {
        "messages": [response]
    }

def get_graph():
    
    builder = StateGraph(MessagesState)
    builder.add_node(call_model)
    builder.add_node(ToolNode(tools))
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges(
        "call_model",
        tools_condition,
    )
    builder.add_edge("tools", "call_model")
    graph = builder.compile()
    return graph
