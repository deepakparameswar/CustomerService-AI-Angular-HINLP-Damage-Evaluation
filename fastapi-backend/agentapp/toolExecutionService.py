import os 
from dotenv import load_dotenv

from typing_extensions import Literal, TypedDict
from langgraph.graph import END, StateGraph, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages

## Reducers
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.prebuilt import tools_condition, ToolNode

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from langchain_core.tools import tool
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.schema import AgentAction
from typing import Dict, List, Optional, Any

import uuid


# Load environment variables from the .env file in the same directory as this script
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

print(f"GROQ_API_KEY: {os.getenv('GROQ_API_KEY')}")

groq_api_key = os.getenv("GROQ_API_KEY")
if groq_api_key:
    os.environ["GROQ_API_KEY"] = groq_api_key
else:
    raise ValueError("GROQ_API_KEY environment variable is not set")


llm = ChatGroq(model="qwen/qwen3-32b", temperature=0)

# Agent prompt template
agent_prompt = PromptTemplate.from_template("""
You are an intelligent assistant that follows a given Standard Operating Procedure (SOP) to decide and execute tools step by step.

Your goals:
1. Always follow the provided SOP exactly — do not assume, infer, or hallucinate any extra steps or tools.
2. Use only the tools listed below. Do not call any tool that is not in the SOP.
3. If this is the first execution (previous tool response is null), start from the first relevant step in the SOP.
4. If the SOP step depends on the previous tool’s result, decide the next tool accordingly.
5. Always interrupt before executing a tool to ask for user approval.

---

**Format to follow strictly:**
SOP: {operating_procedure}

Thought: Explain what step in the SOP should be executed next, and why.
Action: Choose one action (tool) to execute next — must be one of [{tool_names}].

---

**Available tools:**
{tools}

userID: {userID}
previous tool response: {toolRes}

---

Important:
- Execute one tool at a time — do not run multiple tools in a single step.
- Never skip a tool required by the SOP.
- Never make assumptions or create steps outside the SOP.
- Decide whether to call a tool only if it’s required by the SOP and appropriate based on the last tool’s response.
""")


class GraphState(TypedDict):
   operating_procedure: str
   messages: Annotated[Optional[List[any]], add_messages]
   toolRes: Optional[List[any]]
   userID: str

groq_api_key = os.getenv("GROQ_API_KEY")
if groq_api_key:
    os.environ["GROQ_API_KEY"] = groq_api_key
else:
    raise ValueError("GROQ_API_KEY environment variable is not set")


llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)


# In-memory payment data
payment_data = {
    "U001": {"status": "failed", "amount": "₹5000", "date": "2024-01-15", "name": "John Doe"},
    "U002": {"status": "failed", "amount": "₹3000", "date": "2024-01-14", "name": "Jane Smith"},
    "U003": {"status": "pending", "amount": "₹7500", "date": "2024-01-16", "name": "Bob Wilson"}
}

@tool
def get_payment_status(user_id: str) -> dict:
    """Get payment status from API for a user ID."""
    import time
    
    # Simulate API processing time
    time.sleep(1)
    
    # Access payment data directly (simulating API call)
    if user_id in payment_data:
        payment_info = payment_data[user_id]
        return {
            "user_id": user_id,
            "payment_status": payment_info["status"],
            "amount": payment_info["amount"],
            "date": payment_info["date"],
            "user_name": payment_info["name"],
            "api_response_time": "1 second"
        }
    else:
        return {
            "user_id": user_id,
            "payment_status": "failed",
            "error": "Payment record not found",
            "message": f"User ID '{user_id}' not found."
        }

@tool
def check_bank_statement(user_id: str) -> dict:
    """Get bank statement status for a user ID"""
    # return {
    #     "user_id": user_id,
    #     "status": "SUCCESS",
    # }
    return {
        "user_id": user_id,
        "status": "PENDING",
    }

@tool
def create_support_ticket(tool_input: str) -> dict:
    """Create support ticket for user issues. Input should be 'user_id,issue_description'"""
    parts = tool_input.split(',', 1)
    user_id = parts[0].strip()
    issue = parts[1].strip() if len(parts) > 1 else "General issue"
    
    return {
        "ticket_id": f"TKT-{uuid.uuid4().hex[:8].upper()}",
        "user_id": user_id,
        "issue": issue,
        "status": "created",
        "priority": "high"
    }

@tool
def updateUserdetails(user_id: str) -> dict:
    """Update the user secondName for a user ID"""
    return {
        "user_id": user_id,
        "status": "SUCCESS",
    }


# Create LangChain Agent
tools = [
    get_payment_status,
    create_support_ticket,
    check_bank_statement,
    updateUserdetails
]

llm_with_tools = llm.bind_tools(tools)

def assistant(state: GraphState):
    """Plan what actions the agent wants to take"""
    tool_descriptions = "\n".join([f"{tool.name}: {tool.description}" for tool in tools])
    tool_names = ", ".join([tool.name for tool in tools])
    
    prompt_text = agent_prompt.format(
        tools=tool_descriptions,
        tool_names=tool_names,
        operating_procedure=state["operating_procedure"],
        userID= state["userID"],
        toolRes= state.get("toolRes", [])
    )

    print(f"prompt_text >>>>>> : {prompt_text}")

    return {"messages": [llm_with_tools.invoke([prompt_text] + state.get("messages", []))]}


tools_node = ToolNode(tools)

def handle_tool_output(state):
    # Run the ToolNode manually
    tool_result = tools_node.invoke(state)
    
    # ✅ Extract the actual ToolMessage(s)
    tool_messages = tool_result.get("messages", [])
    
    messages = state.get("messages", [])
    messages.extend(tool_messages)  # ✅ add ToolMessages, not a dict

    return {
        **state,
        "toolRes": tool_messages,  # optional, for prompt reference
        "messages": messages
    }



def build_sopGraph():

    #Graph
    workflow = StateGraph(GraphState)
    workflow.add_node("assistant", assistant)
    workflow.add_node("tools", handle_tool_output)
    workflow.add_edge(START, "assistant")

    workflow.add_conditional_edges("assistant", tools_condition)
    workflow.add_edge("tools", "assistant")


    ## Human in the loop and memory
    memory = MemorySaver()
    graph = workflow.compile(interrupt_before=["tools"] ,checkpointer=memory)
    return graph

    
    
