import os

import openai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from postgres_searcher import PostgresSearcher
from rag_flow import RAGFlow

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()


# Define request model
class QuestionRequest(BaseModel):
    question: str


# Initialize OpenAI client
openai_client = openai.AsyncOpenAI(base_url="https://models.inference.ai.azure.com", api_key=os.getenv("GITHUB_TOKEN"))

# Initialize PostgresSearcher
searcher = PostgresSearcher(
    postgres_host=os.environ["POSTGRES_HOST"],
    postgres_username=os.environ["POSTGRES_USERNAME"],
    postgres_database=os.environ["POSTGRES_DATABASE"],
    postgres_password=os.environ.get("POSTGRES_PASSWORD"),
    openai_embed_client=openai_client,
    embed_model="text-embedding-3-small",
    embed_dimensions=256,
)

# Initialize RAGFlow
rag_flow = RAGFlow(searcher=searcher, openai_chat_client=openai_client, chat_model="gpt-4o-mini")


# Define the RAG function
async def do_rag(question: str):
    response = await rag_flow.answer(original_user_query=question, past_messages=[])
    return response


# Define the FastAPI endpoint
class Message(BaseModel):
    content: str
    role: str


class ChatRequest(BaseModel):
    messages: list[Message] = Field(example=[{"role": "user", "content": "Any climbing gear?"}])


@app.post("/chat")
async def ask_question(request: ChatRequest):
    try:
        user_message = next((msg.content for msg in request.messages if msg.role == "user"), None)
        if not user_message:
            raise HTTPException(status_code=400, detail="No user message found in the request.")

        response = await do_rag(user_message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Run the app with Uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
