import os 
from dotenv import load_dotenv
from typing_extensions import Literal, TypedDict
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from typing import List, Optional
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated, List
from langgraph.graph.message import add_messages, BaseMessage
from langgraph.checkpoint.memory import MemorySaver, InMemorySaver

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


from langchain_community.tools.tavily_search import TavilySearchResults



from langchain_core.output_parsers import StrOutputParser

import random
from pathlib import Path
import json

from langgraph.graph import END, StateGraph, START

from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from pydantic import BaseModel, Field

from langchain_core.documents import Document


# Load environment variables from the .env file in the same directory as this script
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from langchain_groq import ChatGroq

# print(f"GROQ_API_KEY: {os.getenv('GROQ_API_KEY')}")

groq_api_key = os.getenv("GROQ_API_KEY")
if groq_api_key:
    os.environ["GROQ_API_KEY"] = groq_api_key
else:
    raise ValueError("GROQ_API_KEY environment variable is not set")

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

# Schema for structured output to use as routing logic
class Route(BaseModel):
    step: Literal["rag_search", "issue_analyser"] = Field(description="The next step in the routing process")
    type: Literal["issue", "query"] = Field(description="The type of the input")

# Schema for structured output to use as analysis state
class IssueState(BaseModel):
    """
    Represent the state of issue analyser
    """
    validIssue: bool = Field(description="Whether the user query is valid or not.")
    missingProperties: List[str] = Field(description="Extracted missing properties.")
    issueProblemDesc: Optional[str] = Field(default=None, description="The problem description.")
    policyNumber: Optional[str] = Field(default=None, description="The policy number.")

## Augment the LLM with schema for structured output
router = llm.with_structured_output(Route)

## 
analyser_llm = llm.with_structured_output(IssueState)

class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        documents: list of documents
        decision: decision taken by supervisor
        type: type of the user query
    """

    question: str
    generation: str
    documents: List[str]
    decision: str
    type: str
    vectorDecision: str
    missingProperties: Optional[List[str]]
    issueProblemDesc: Optional[str]
    policyNumber: Optional[str]
    validIssue: bool


# Router node
def supervisor(state):
    """Route the question to the appropriate node"""
    prompt = f"""
                Route the input to rag_search,issue_analyser based on the user's request.
                if the input is an problem statement then set decision as issue_analyser and type as issue.
                Or if the input is some query then set decision as rag_search and type as query"""
    descision = router.invoke(
        [
            SystemMessage(
                content=prompt
            ),
            HumanMessage(content=state["question"])
        ]
    )
    print(f"descision >>>>>>>>>>>. : {descision}")
    return {"decision": descision.step, "type": descision.type}


# Issue analyser node
def issue_analyser(state):
    """Analyse the user issue to provide the better resolution to the user"""
    prompt = f"""
        Analyse the input and verify if it is relevant to the LIC system based on the user's request.

        Rules:
        1. Extract policyNumber if present, else set to null.
        2. Extract problem description if present, else set to null.
        3. If both policyNumber and issueProblemDesc are not null, set validIssue = true, else set validIssue = false.
        4. missingProperties must ALWAYS include the names of all keys where the value is null.
        - If policyNumber = null, then add "policyNumber" to missingProperties.
        - If issueProblemDesc = null, then add "issueProblemDesc" to missingProperties.
        - If neither is null, missingProperties must be an empty array [].
        5. Return the result strictly in JSON format with keys:
        ["validIssue", "missingProperties", "issueProblemDesc", "policyNumber"].
        """
    
    result = analyser_llm.invoke([
            SystemMessage(
                content=prompt
            ),
            HumanMessage(content=state["question"])
    ])
    
    print(f"issue_analyser >>>>>>>>>>>. : {result}")
    return {"validIssue": result.validIssue, "missingProperties": result.missingProperties, "issueProblemDesc": result.issueProblemDesc, "policyNumber": result.policyNumber}
    

# conditional edge function(also we can call as condition function) to route to the appropriate node
def route_decision(state):

    # Return the node name we want to visit next
    if state["decision"] == "rag_search":
        return "rag_route"
    elif state["decision"] == "issue_analyser":
        return "issue_analyser"


persist_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_db")

# Initialize OpenAI embeddings
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Initialize Chroma vectorstore with persistent directory
vectorstore = Chroma(
    collection_name="life_queries",
    embedding_function=embedding_model,
    persist_directory=persist_directory
)

# Initialize Chroma vectorstore with persistent directory
issue_sop_vectorstore = Chroma(
    collection_name="life_issue_sop",
    embedding_function=embedding_model,
    persist_directory=persist_directory
)


# Data model
class RouteQuery(BaseModel):
    """Route a user query to modest relevant datasource."""

    datasource: Literal["vectorstore", "web_search", "issue_sop_vectorstore"] = Field(
        ...,
        description = "Given a user question choose to route it to web search or a vectorstore"
    )

# LLM with function call
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
structured_llm_router = llm.with_structured_output(RouteQuery)

# Prompt
system = """You are an expert at routing a user question to a vectorstore or web search.
            The vectorstore contains documents related to LIC FAQs.
            The issue_sop_vectorstore contains documents related to User issues like payment failure or name change or some support queries.
            Use the vectorstore for questions on the topics. Otherwise, use web-search."""


route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)

question_router = route_prompt | structured_llm_router

## Retrieval Grader

# Data model
class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: Literal["yes", "no"] = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )


## LLM with function call
grader_llm = ChatGroq(model="llama-3.3-70B-versatile", temperature=0)
structured_llm_grader = grader_llm.with_structured_output(GradeDocuments)

# Prompt
system = """ You are a grader assessing relevance of a retrieved document to a user question. \n
            If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
            It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
            Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question.
            IMPORTANT: look into the context of the document for the given question, if its best fit then with that conext then we can grade it as valid else not valid"""

grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Retrieved document: \n\n {document} \n\n User question: {question} \n")
    ]
)

retrieval_grader = grade_prompt | structured_llm_grader


## Generate

# Prompt
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an assistant for question-answering tasks. Use ONLY the retrieved context to answer the question. Do not add any information beyond what is provided in the context. If the context doesn't contain the answer, say 'I don't have enough information to answer this question.' Keep the answer concise and within three sentences. if multy steps involved then try to order like 1, 2 etc.."),
        ("human", "Question: {question}\n\nContext: {context}\n\nAnswer:")
    ]
)

# LLM
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

# Post-processing
# def format_docs(doc_txt):
#     return "\n\n".join(doc.page_content for doc in docs)

# Chain
rag_chain = prompt | llm | StrOutputParser()



## Hallucination Grader

# Data model
class GradeHallucination(BaseModel):
    """Binary score for hallucination present in generation answer."""

    binary_score: Literal["yes", "no"] = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )

# LLM with function call
llm = ChatGroq(model="llama-3.3-70B-versatile", temperature=0)
structured_llm_grader = llm.with_structured_output(GradeHallucination)

# Prompt
system = """
You are a grounding validator for a retrieval-augmented generation system.

Give a binary score: 'yes' or 'no'.

Mark 'yes' if:
- The response aligns with the intent, workflow, or purpose of the retrieved content.
- The response correctly applies or explains the SOP steps, even if details are inferred.
- The response stays within the same domain and does not invent new processes.

Mark 'no' ONLY if:
- The response clearly fabricates APIs, policies, or steps not present.
- The response contradicts the retrieved workflow.
- The response discusses a different problem or domain.

Guidance:
- Prefer 'yes' when the response reasonably follows from the retrieved facts.
- Do not require verbatim matching.
- Logical continuation is allowed.
"""


hallucination_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation} \n")
    ]
)

hallucincation_grader = hallucination_prompt | structured_llm_grader


## Answer Grader

# Data model
class GradeAnswer(BaseModel):
    """Binary score to assess answer address question."""

    binary_score: Literal["yes", "no"] = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )

# LLM with function call
answer_prompt_llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
structured_llm_grader = answer_prompt_llm.with_structured_output(GradeAnswer)

# Prompt
system = """You are a grader evaluating whether the provided content is RELEVANT and ACCEPTABLE
for resolving the user's issue.

The system supports multiple predefined issues with SOP-based solutions, such as:
- insurance payment status issues
- updating policy holder details (name, address)
- accident-related vehicle damage estimation

Grading rules:

1. Focus on USER INTENT, not exact wording.
2. If the content matches the SAME ISSUE CATEGORY as the user question, it is relevant.
3. Procedural answers, SOP steps, or API calls are VALID final answers.
4. The content does NOT need to fully resolve the issue; providing correct NEXT STEPS is sufficient.
5. Do NOT reject answers just because they are technical, short, or action-oriented.

Answer YES if:
- the content addresses the same problem domain as the user's question, AND
- the steps or information would help progress or resolve the issue.

Answer NO only if:
- the content belongs to a completely different issue, OR
- it provides no useful or actionable information.

IMPORTANT:
- SOP execution steps are terminal answers.
- Do not expect explanations or summaries.
- Do not penalize answers that rely on external APIs or tools.

Return ONLY 'yes' or 'no'.
"""

answer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "User question: \n\n {question} \n\n LLM answer: {generation} \n")
    ]
)

answer_grader = answer_prompt | structured_llm_grader

## Question Re-writer

# LLM
question_rewriter_llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

# prompt
system = """You are a question re-writer that converts an input question to a better version optimized for vectorstore retrieval.

Your task:
- Extract the core intent and key concepts from the question
- Rephrase it to be more specific and focused
- Use keywords that would match relevant documents
- Keep it concise and clear
- Return ONLY the improved question, nothing else"""

re_write_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        (
            "human", 
            "Original question: {question}\n\nImproved question:"
        )
    ]
)

question_rewriter = re_write_prompt | question_rewriter_llm | StrOutputParser()

web_search_tool = TavilySearchResults(k=3)

def retrieve(state):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """

    print("---RETRIEVE---")

    question = state["question"]

    # default vector store
    store = vectorstore
    filter = {"category": "life-query"}

    # issue sop vector store
    if state["type"] == "issue" and state["validIssue"] == True:
        store = issue_sop_vectorstore
        filter = {"category": "life_issue_sop"}
        question = state["issueProblemDesc"]

    ## context
    documents = store.similarity_search(
            question,
            k=3,
            filter=filter
        )

    print(f"docs: {documents}")

    return {"documents": documents, "question": question}

def generate(state):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """

    print("---GENERATE---")

    question = state["question"]
    documents = state["documents"]

    # Prompt
    generation = rag_chain.invoke({"context": documents, "question": question})

    return {"documents": documents, "question": question, "generation": generation}

def grade_documents(state):
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with only filtered relevant documents
    """

    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")

    question = state["question"]
    documents = state["documents"]

    print(f"question: {question}")
    print(f"documents: {documents}")

    # Score each doc
    filtered_docs = []

    for doc in documents:
        score = retrieval_grader.invoke(
            {
                "question": question,
                "document": doc.page_content
            }
        )

        print(f"grade_documents score: {score}")

        grade = score.binary_score

        print(f"grade_documents grade: {grade}")

        if grade == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(doc)
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            continue

    return {"documents": filtered_docs, "question": question}

def transform_query(state):
    """
    Transform the query to produce a better question. The re-phrased question is very small and crisp better suited for retrieval.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates question key with a re-phrased question
    """

    print("---TRANSFORM QUERY---")

    question = state["question"]
    documents = state["documents"]

    # We assume that this is a function
    better_question = question_rewriter.invoke(
        {
            "question": question
        }
    )

    return {"documents": documents, "question": better_question}

def web_search(state):
    """
    Web search based on the re-phrased question

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with appended web results
    """

    print("---WEB SEARCH---")

    question = state["question"]

    # Web search
    docs = web_search_tool.invoke({"query": question})

    web_results = "\n".join([d["content"] for d in docs])

    web_results = Document(page_content=web_results)


    return {"documents": web_results, "question": question}

def ragDecision(state):
    """
    RAG decision making node

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): set vectorDecision to decide whether to go for websearch or vector store check
    """

    print("---RAG DECISION---")

    question = state["question"]

    source = question_router.invoke(
        {
            "question": question
        }
    )

    print(f"source : >>>>>>> ", source)

    return {"vectorDecision": source.datasource, "question": question}


## Edges ##

def rag_route_question(state):

    """
    Route question to web search or RAG.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    print("---ROUTE QUESTION---")
    print(f"state: {state}")

    if state["vectorDecision"] == "web_search":
        print("---ROUTE QUESTION TO WEB SEARCH---")
        return "web_search"

    elif state["vectorDecision"] == "vectorstore" or state["vectorDecision"] == "issue_sop_vectorstore":
        print("---ROUTE TO QUESTION TO RAG---")
        return "vectorstore"
    
def decide_to_generate(state):
    """
    Determines whether to generate an answer, or re-generate a question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Binary decision for next node to call
    """

    print("---ASSESS GRADED DOCUMENTS---")

    state["question"]

    filtered_documents = state["documents"]

    if not filtered_documents:

        # All documents have filtered check_relevance
        # We will re-generate a new query
        print("---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---")
        
        return "transform_query"

    else:
        # We have relevant documents, so generate answer
        print("---DECISION: GENERATE---")
        return "generate"
    

def grade_generation_v_documents_and_answers(state):
    """
    Determines whether the generation and documents and answers are grounded.

    Args:
        state (dict): The current graph state
    
    Returns:
        str: Decision for next node to call

    """

    print("---CHECK HALLUCINATIONS---")

    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    print(f"question: {question}")
    print(f"documents: {documents}")
    print(f"generation: {generation}")

    score = hallucincation_grader.invoke(
        {
            "documents": documents,
            "generation": generation
        }
    )

    grade = score.binary_score

    print(f"hallucination score: {score}")
    print(f"hallucination grade: {grade}")

    # Check hallucination
    if grade == "yes":

        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")

        # Check question-answering
        print("---GRADE GENERATION VS QUESTION---")

        score = answer_grader.invoke(
            {
                "question": question,
                "generation": generation
            }
        )
        grade = score.binary_score
        print(f"answer score: {score}")

        if grade == "yes":
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "notUseful"
    else:
        print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "notSupported"
    
def taskcreation_condition(state):
    """
    Route to task_creator node, task_creator node will create the task for us 

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    print("---ROUTE TASK CREATION---")

    if state["validIssue"] == True:
        if state["policyNumber"] != None and state["issueProblemDesc"] != None:
            print("---VALID ISSUE TO CALL TOOL---")
            return "rag_route"
    else:
        print("---NOT AN VALID ISSUE TO CALL TOOL---")
        return "notValid"

def build_graph():

    workflow = StateGraph(GraphState)

    # Define the nodes
    workflow.add_node("supervisor", supervisor) # Decision maker node(root router)
    workflow.add_node("rag_route", ragDecision)  # route question
    workflow.add_node("web_search", web_search)  # web search
    workflow.add_node("issue_analyser", issue_analyser) # issue analyser
    workflow.add_node("retrieve", retrieve)  # retrieve
    workflow.add_node("grade_documents", grade_documents)  # grade documents
    workflow.add_node("generate", generate)  # generate
    workflow.add_node("transform_query", transform_query) # transform_query

    # Chat Assistant
    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        route_decision,
        {
            # Name returned by route_decision : Name of next node to visit

            "rag_route":"rag_route",
            "issue_analyser": "issue_analyser"
        }
    )
    workflow.add_conditional_edges(
        "issue_analyser",
        taskcreation_condition,
        {
            "rag_route":"rag_route",
            "notValid": END
        }
    )

    # Build graph
    workflow.add_conditional_edges(
        "rag_route",
        rag_route_question,
        {
            "web_search": "web_search",
            "vectorstore": "retrieve"
        }
    )

    workflow.add_edge("web_search", "generate")
    workflow.add_edge("retrieve", "grade_documents")

    workflow.add_conditional_edges(
        "grade_documents",
        decide_to_generate,
        {
            "transform_query": "transform_query",
            "generate": "generate"
        }
    )

    workflow.add_edge("transform_query", "retrieve")

    workflow.add_conditional_edges(
        "generate",
        grade_generation_v_documents_and_answers,
        {
            "useful": END,
            "notUseful": "transform_query",
            "notSupported": "transform_query"
        }
    )

    # Compile
    graph = workflow.compile()

    return graph