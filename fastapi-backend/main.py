from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import os
from agentapp.customerService import build_graph

from agentapp.toolExecutionService import build_sopGraph

graph = build_graph()
sopGraph = build_sopGraph()
app = FastAPI()

# Mount static files
app.mount("/images", StaticFiles(directory="images"), name="images")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Issue(BaseModel):
    userID: str
    userName: str
    issueDescription: str
    issueTitle: str
    threadID: str
    imageURL: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    token: str = None

class StartExecutionRequest(BaseModel):
    issueDescription: str

class sopQuery(BaseModel):
    operating_procedure: str
    userID: str
    threadID: str
    imageURL: Optional[str] = None


payment_status_data = [
    {"userID": "U001", "paymentStatus": "Pending", "policyNumber": "12345", "amount": 1500.00},
    {"userID": "U002", "paymentStatus": "Completed", "policyNumber": "12346", "amount": 2200.50},
    {"userID": "U003", "paymentStatus": "Failed", "policyNumber": "12347", "amount": 800.75},
    {"userID": "U004", "paymentStatus": "Processing", "policyNumber": "12348", "amount": 3100.25},
    {"userID": "U005", "paymentStatus": "Completed", "policyNumber": "12349", "amount": 950.00},
    {"userID": "U006", "paymentStatus": "Pending", "policyNumber": "12350", "amount": 1750.80}
]

transaction_documents = [
    {"userID": "U001", "transactionID": "TXN001", "transactionStatus": "Pending", "documentType": "Payment Receipt", "documentID": "DOC12345", "createdDate": "2024-01-15", "lastUpdated": "2024-01-16"},
    {"userID": "U002", "transactionID": "TXN002", "transactionStatus": "Completed", "documentType": "Payment Confirmation", "documentID": "DOC12346", "createdDate": "2024-01-14", "lastUpdated": "2024-01-15"},
    {"userID": "U003", "transactionID": "TXN003", "transactionStatus": "Failed", "documentType": "Payment Failure Notice", "documentID": "DOC12347", "createdDate": "2024-01-13", "lastUpdated": "2024-01-14"},
    {"userID": "U004", "transactionID": "TXN004", "transactionStatus": "Processing", "documentType": "Payment Processing", "documentID": "DOC12348", "createdDate": "2024-01-16", "lastUpdated": "2024-01-16"},
    {"userID": "U005", "transactionID": "TXN005", "transactionStatus": "Completed", "documentType": "Payment Receipt", "documentID": "DOC12349", "createdDate": "2024-01-12", "lastUpdated": "2024-01-13"},
    {"userID": "U006", "transactionID": "TXN006", "transactionStatus": "Pending", "documentType": "Payment Authorization", "documentID": "DOC12350", "createdDate": "2024-01-17", "lastUpdated": "2024-01-17"}
]

issues_data = [
    {"userID": "U001", "userName": "John Doe", "issueDescription": "Payment status not reflected for policy 12345", "issueTitle": "Payment Issue", "threadID": "c10b26e3-9466-4c7a-9130-37f2ec18e558"},
    {"userID": "U002", "userName": "Jane Smith", "issueDescription": "Need some correction for second name from policy 12324", "issueTitle": "Update Second Name", "threadID": "cfb8dcf3-3f2f-4a47-bef5-3cfbc495fc1b"},
    {"userID": "U003", "userName": "Mike Johnson", "issueDescription": "Data export functionality broken", "issueTitle": "Export Bug", "threadID": "d4a93904-99df-4b20-9b34-06a01391c5a5"},
    {"userID": "U004", "userName": "Sarah Wilson", "issueDescription": "My Car get crashed, Please help to get some estimations and the policy number is 671289", "issueTitle": "Car Damage Estimation", "threadID": "1de03fa9-96a1-4988-9989-54b8dcd4a9f1", "imageURL": "http://localhost:8000/images/accident-damage-car.jpg"},
    {"userID": "U005", "userName": "David Brown", "issueDescription": "Page loading very slowly", "issueTitle": "Performance Issue", "threadID": "4a33b890-3028-4204-8f42-1dc469ccf214"},
    {"userID": "U006", "userName": "Lisa Garcia", "issueDescription": "Cannot upload files", "issueTitle": "Upload Error", "threadID": "2ff2a7e7-6f05-4a6b-b406-d5a99f6d7f7d"},
    {"userID": "U007", "userName": "Robert Taylor", "issueDescription": "Search function returns no results", "issueTitle": "Search Bug", "threadID": "db44e64d-cb41-42a4-8b64-982046f06e8a"},
    {"userID": "U008", "userName": "Emily Davis", "issueDescription": "Profile picture not displaying", "issueTitle": "Display Issue", "threadID": "9b8a5410-3cdb-4fd7-85e3-1d57a2e357a8"},
    {"userID": "U009", "userName": "James Miller", "issueDescription": "Password reset not working", "issueTitle": "Reset Error", "threadID": "b92857e4-8db2-4958-b0a7-b6151b3d841a"},
    {"userID": "U010", "userName": "Maria Rodriguez", "issueDescription": "Mobile app crashes on startup", "issueTitle": "Crash Bug", "threadID": "f53d96bb-4972-4b56-b62e-55a497e2123e"},
    {"userID": "U011", "userName": "Kevin Lee", "issueDescription": "Data synchronization failed", "issueTitle": "Sync Error", "threadID": "4b41ff94-4c3e-47ab-bbf5-c00e33f6c8cb"},
    {"userID": "U012", "userName": "Amanda White", "issueDescription": "Report generation timeout", "issueTitle": "Timeout Issue", "threadID": "fbc5013a-7e0a-45cb-9e2a-49707332c5f1"},
    {"userID": "U013", "userName": "Christopher Hall", "issueDescription": "API response returning 500 error", "issueTitle": "API Error", "threadID": "ae7a4bc4-4ee7-43b3-8d79-29b1e1c8ef83"},
    {"userID": "U014", "userName": "Jessica Young", "issueDescription": "Calendar events not saving", "issueTitle": "Save Bug", "threadID": "ed1df00e-d5f7-4048-805a-287c6463038b"},
    {"userID": "U015", "userName": "Daniel King", "issueDescription": "Notification settings reset automatically", "issueTitle": "Settings Issue", "threadID": "3d0b4a19-f74f-4146-8e19-d2fc91b9f81b"},
    {"userID": "U016", "userName": "Ashley Wright", "issueDescription": "Chart data not updating", "issueTitle": "Chart Bug", "threadID": "0e2298c5-85de-4c52-b0c5-cb9f6e03f94d"},
    {"userID": "U017", "userName": "Matthew Lopez", "issueDescription": "User permissions not applied correctly", "issueTitle": "Permission Error", "threadID": "b74e13cf-5db7-4b37-9d25-5f532999f272"},
    {"userID": "U018", "userName": "Stephanie Hill", "issueDescription": "Form validation errors", "issueTitle": "Validation Bug", "threadID": "9fd71258-671c-4a3a-9023-3bb8d49e36e1"},
    {"userID": "U019", "userName": "Andrew Scott", "issueDescription": "Database connection timeout", "issueTitle": "DB Error", "threadID": "a5748705-ff17-4ee0-bc87-0e0a0fa87f22"},
    {"userID": "U020", "userName": "Rachel Green", "issueDescription": "Print functionality not working", "issueTitle": "Print Issue", "threadID": "38f927f5-b1b3-46c2-bfd2-c1ee7e0c6e6a"},
    {"userID": "U021", "userName": "Joshua Adams", "issueDescription": "Theme settings not persisting", "issueTitle": "Theme Bug", "threadID": "4e134918-5b7d-4629-a2da-b4380e8a0533"},
    {"userID": "U022", "userName": "Nicole Baker", "issueDescription": "Backup process failing", "issueTitle": "Backup Error", "threadID": "da15e8c7-3d37-4935-b87e-dc2323b02e13"},
    {"userID": "U023", "userName": "Ryan Gonzalez", "issueDescription": "Language translation missing", "issueTitle": "Translation Issue", "threadID": "ccf44b90-6b37-4d19-9c5e-bb41df58c8f5"},
    {"userID": "U024", "userName": "Megan Nelson", "issueDescription": "Video playback stuttering", "issueTitle": "Video Bug", "threadID": "e99ef2bc-60a2-4c5a-987b-6dc038a06b57"},
    {"userID": "U025", "userName": "Brandon Carter", "issueDescription": "Shopping cart items disappearing", "issueTitle": "Cart Error", "threadID": "1ac9f26a-0e09-4a20-9b2d-4241b31d9e8f"},
    {"userID": "U026", "userName": "Samantha Mitchell", "issueDescription": "Two-factor authentication failing", "issueTitle": "2FA Issue", "threadID": "94854c8e-d9b7-4f9c-b59e-ec31d5ad4c8f"},
    {"userID": "U027", "userName": "Justin Perez", "issueDescription": "Image compression quality poor", "issueTitle": "Image Bug", "threadID": "7b82d8de-5c1e-4ed7-8c06-1c059dbbb8b4"},
    {"userID": "U028", "userName": "Brittany Roberts", "issueDescription": "Keyboard shortcuts not responding", "issueTitle": "Shortcut Error", "threadID": "858c273b-f192-4d33-8c76-84d7c5b0b5e3"},
    {"userID": "U029", "userName": "Tyler Turner", "issueDescription": "Auto-save feature not working", "issueTitle": "Save Issue", "threadID": "c1b7b4e2-1f77-4c74-bb1f-02a97b77dc2a"},
    {"userID": "U030", "userName": "Kayla Phillips", "issueDescription": "Social media integration broken", "issueTitle": "Social Bug", "threadID": "f8cccf6c-72d0-4d15-8f1a-68013a002dc7"},
    {"userID": "U031", "userName": "Nathan Campbell", "issueDescription": "Memory usage extremely high", "issueTitle": "Memory Issue", "threadID": "ea5c4905-7761-4848-bef0-6df40361e995"},
    {"userID": "U032", "userName": "Alexis Parker", "issueDescription": "Drag and drop not functioning", "issueTitle": "DnD Error", "threadID": "63b3e5e7-53c9-4969-9a9a-356f51211b3f"},
    {"userID": "U033", "userName": "Jordan Evans", "issueDescription": "Timezone conversion incorrect", "issueTitle": "Timezone Bug", "threadID": "7c54f8ab-0f21-4f64-bb8b-b60cbf3ac52b"},
    {"userID": "U034", "userName": "Taylor Edwards", "issueDescription": "Batch processing stuck", "issueTitle": "Batch Issue", "threadID": "16ffb93b-9c25-4b07-b0a0-2b86703b6c2e"},
    {"userID": "U035", "userName": "Morgan Collins", "issueDescription": "SSL certificate expired", "issueTitle": "SSL Error", "threadID": "d83cc3d3-1f5a-4f5e-9f4b-7c97b00c1c86"},
    {"userID": "U036", "userName": "Casey Stewart", "issueDescription": "Pagination not working correctly", "issueTitle": "Pagination Bug", "threadID": "e53a7b91-5cc7-4df7-bf2a-1c4816c78542"},
    {"userID": "U037", "userName": "Alex Sanchez", "issueDescription": "Webhook delivery failing", "issueTitle": "Webhook Issue", "threadID": "4b69e08d-0c55-4931-894c-6508d72db376"},
    {"userID": "U038", "userName": "Jamie Morris", "issueDescription": "Cache invalidation problems", "issueTitle": "Cache Error", "threadID": "8c6cc2c4-7cf3-4f73-bf6c-f0b2a3c49bda"},
    {"userID": "U039", "userName": "Riley Rogers", "issueDescription": "File permissions too restrictive", "issueTitle": "Permission Bug", "threadID": "f239a29f-24d1-4c73-9466-056d6cbf8d55"},
    {"userID": "U040", "userName": "Avery Reed", "issueDescription": "Scheduled tasks not running", "issueTitle": "Scheduler Issue", "threadID": "c8201bfb-7829-4b4f-b5d5-cf429d4c03f4"},
    {"userID": "U041", "userName": "Quinn Cook", "issueDescription": "Load balancer health check failing", "issueTitle": "LB Error", "threadID": "50439c24-e1e2-43c5-b169-4447ce19751c"},
    {"userID": "U042", "userName": "Sage Bailey", "issueDescription": "Session timeout too aggressive", "issueTitle": "Session Bug", "threadID": "e8f90547-0b8c-49a0-bdbe-71e76dbb92ba"},
    {"userID": "U043", "userName": "River Rivera", "issueDescription": "Audit log entries missing", "issueTitle": "Audit Issue", "threadID": "dbda19ef-4d23-4c66-9345-00d06db02c58"},
    {"userID": "U044", "userName": "Phoenix Cooper", "issueDescription": "Rate limiting too strict", "issueTitle": "Rate Error", "threadID": "dfbc8e50-c37d-465c-9366-31e9309ad12a"},
    {"userID": "U045", "userName": "Skylar Richardson", "issueDescription": "Geolocation services unavailable", "issueTitle": "Location Bug", "threadID": "f836f8e4-e792-44df-8c6f-223abbd7f577"},
    {"userID": "U046", "userName": "Dakota Cox", "issueDescription": "Encryption key rotation failed", "issueTitle": "Crypto Issue", "threadID": "a24fcff7-d3a8-4405-9407-59cb8a7a2dcf"},
    {"userID": "U047", "userName": "Rowan Ward", "issueDescription": "Microservice communication timeout", "issueTitle": "Service Error", "threadID": "e43d0a52-7e0a-4f45-bacb-5f8eeb8a8cfd"},
    {"userID": "U048", "userName": "Sage Torres", "issueDescription": "Container orchestration failing", "issueTitle": "Container Bug", "threadID": "f4de7ae0-309a-40e8-bc13-b97a6031a52a"},
    {"userID": "U049", "userName": "Finley Peterson", "issueDescription": "Message queue overflow", "issueTitle": "Queue Issue", "threadID": "3a6e46e9-4528-40db-9f4b-b367685f90c6"},
    {"userID": "U050", "userName": "Emery Gray", "issueDescription": "CDN cache not updating", "issueTitle": "CDN Error", "threadID": "1fd6ad94-30a6-46fc-bb20-8c93900d83b2"}
]


class ApprovalRequest(BaseModel):
    threadID: str
    approved: bool
    feedback: Optional[str] = None

@app.options("/issues")
async def options_issues():
    return Response(status_code=200)

@app.options("/login")
async def options_login():
    return Response(status_code=200)

@app.options("/start-execution")
async def options_start_execution():
    return Response(status_code=200)

@app.options("/process-query")
async def options_process_sopquery():
    return Response(status_code=200)

@app.options("/outputs/{path:path}")
async def options_outputs():
    return Response(status_code=200)

@app.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    # Debug logging
    print(f"Received username: '{request.username}', password: '{request.password}'")
    
    # Hardcoded credentials
    if request.username == "admin" and request.password == "password":
        return LoginResponse(
            success=True,
            message="Login successful",
            token="dummy-jwt-token-123"
        )
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

@app.get("/")
async def root():
    return {"message": "FastAPI server is running"}

@app.get("/issues", response_model=List[Issue])
async def get_issues():
    return issues_data


@app.post("/process-sopquery")
async def process_sopquery(request: sopQuery):
    print(f"SOP Execution started for sop: {request.operating_procedure}")

    thread = {"configurable": {"thread_id": request.threadID}}
    query = {"operating_procedure": request.operating_procedure, "userID": request.userID, "imageURL": request.imageURL}

    response = sopGraph.invoke(query, thread)

    print(f"SOP sopquery invocation response: {response}")

    latest_messages = response["messages"]

    latest_message = latest_messages[-1]  # the most recent message
    print(f"latest_message: >>>>>>>>> {latest_message}")

    # Check for tool_calls
    tool_calls = latest_message.additional_kwargs.get("tool_calls", [])

    toolRes = tool_calls[-1]

    print(f"tool calls: {tool_calls}")

    if tool_calls:
        # Extract tool names
        tool_names = [t["function"]["name"] for t in tool_calls if "function" in t]
        tool_arguments = [t["function"]["arguments"] for t in tool_calls if "function" in t]
        print(f"tool_names: >>>>>>>>> {tool_names}")
        toolRes["tool_name"] = tool_names[-1]
        toolRes["tool_arguments"] = tool_arguments[-1]
        print("Tool calls found:", tool_names[-1])
        print("Tool calls found:", tool_arguments[-1])
    else:
        print("No tool calls found.")

    
    return {"status": "success", "message": "SOP execution started", "response": toolRes}

@app.post("/start-execution")
async def start_execution(request: StartExecutionRequest):
    print(f"SOP Execution started for issue: {request.issueDescription}")
    response = graph.invoke({"question": request.issueDescription})
    print(f"SOP graph invocation response: {response}")
    return {"status": "success", "message": "SOP execution started", "response": response}

@app.get("/getPaymentStatus/{userID}")
async def get_payment_status(userID: str):
    payment_info = next((item for item in payment_status_data if item["userID"] == userID), None)
    if payment_info:
        return payment_info
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.get("/getTransactionDoc/{userID}")
async def get_transaction_doc(userID: str):
    transaction_doc = next((item for item in transaction_documents if item["userID"] == userID), None)
    if transaction_doc:
        return transaction_doc
    else:
        raise HTTPException(status_code=404, detail="Transaction document not found for user")

# @app.get("/executions/pending")
# async def get_pending_execution_endpoint():
#     """Get all pending tool executions"""
#     all_executions = get_pending_executions()
#     print(f"agent_sessions: >>>>>>>>>> {agent_sessions}")
#     return all_executions

@app.post("/executions/approve")
async def approve_execution_endpoint(request: ApprovalRequest):
    """Approve or reject tool execution"""

    print(f"Received approval request: {request}")
    
    if request.threadID == None:
        raise HTTPException(status_code=404, detail="threadID not found")

    thread = {"configurable": {"thread_id": request.threadID}}

    response = sopGraph.invoke(None, thread, stream_mode="values")

    print(f"response: >>>>>>  {response}")

    # Get messages list
    latest_messages = response["messages"]

    # Get the latest message (last one)
    latest_message = latest_messages[-1]
    print("Latest message:", latest_message)

    # Safely check for tool_calls
    tool_calls = latest_message.additional_kwargs.get("tool_calls", [])

    toolRes = {}

    if tool_calls:
        # Get the most recent tool call
        latest_tool_call = tool_calls[-1]
        tool_name = latest_tool_call["function"]["name"]
        tool_arguments = latest_tool_call["function"]["arguments"]
        print("Tool name:", tool_name)
        print("Tool Args:", tool_arguments)

        #Tool reseponse
        latest_tool_res = response["toolRes"][-1] if response.get("toolRes") else {}

        print(f"tool calls: {latest_tool_call}")
        print(f"tool_name: {tool_name}")
        print(f"latest_tool_res: {latest_tool_res}")

        toolRes = latest_tool_call if latest_tool_call else {}
        toolRes["tool_name"] = tool_name if tool_name else None
        toolRes["tool_arguments"] = tool_arguments if tool_arguments else None
        toolRes["previous_tool_res"] = latest_tool_res if latest_tool_res else None
        toolRes["hasNextTool"] = True
        
    else:
        #Tool reseponse
        latest_tool_res = response["toolRes"][-1] if response.get("toolRes") else {}
        toolRes["previous_tool_res"] = latest_tool_res if latest_tool_res else None
        toolRes["hasNextTool"] = False
        print("No tool_calls found in the latest message.")


    return toolRes

if __name__ == "__main__":
    import uvicorn
    import signal
    import sys
    
    def signal_handler(sig, frame):
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        pass