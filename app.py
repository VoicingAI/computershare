# api_endpoint.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import uuid
import asyncio

from langchain_core.messages import ToolMessage, HumanMessage
from agent.graph import compile_langgraph_workflow

load_dotenv()

app = FastAPI(title="LangChain API Endpoint")

# Compile the langgraph workflow once at startup
graph = compile_langgraph_workflow()

class RequestPayload(BaseModel):
    session_id: str
    message: str

class ResponsePayload(BaseModel):
    session_id: str
    response: str
    execution_time: float

@app.post("/process", response_model=ResponsePayload)
async def process_message(payload: RequestPayload):
    session_id = payload.session_id
    message = payload.message

    # Use session_id as thread_id
    config = {
        "configurable": {
            "thread_id": session_id,
        }
    }

    inputs = {"messages": ("human", message)}
    collected_chunks = []
    start_time = asyncio.get_event_loop().time()

    try:
        async for chunk in graph.astream_events(inputs, config, version="v1"):
            if chunk['event'] == "on_chat_model_stream":
                content = chunk['data']['chunk'].content
                collected_chunks.append(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    end_time = asyncio.get_event_loop().time()
    execution_time = end_time - start_time

    result = ''.join(collected_chunks)

    return ResponsePayload(
        session_id=session_id,
        response=result,
        execution_time=execution_time
    )


if __name__ == "__main__":
    import uvicorn
    # Optionally, you can set host and port as variables
    host = "0.0.0.0"
    port = 8000

    # Run the uvicorn server programmatically
    uvicorn.run(
        "app:app",  # Module name and app instance
        host=host,
        port=port,
        reload=True,  # Enable auto-reload; set to False in production
        log_level="info"
    )


