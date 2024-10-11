import os

import openai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List

from postgres_searcher import PostgresSearcher
from rag_flow import RAGFlow

app = FastAPI()


class Message(BaseModel):
    content: str
    role: str



class QueryRequest(BaseModel):
    messages: List[Message] = Field(
        ...,
        example=[
            {"content": "Best shoe for hiking?", "role": "user"}
        ]
    )

async def do_rag(messages: list[dict[str, str]]):
    load_dotenv()
    openai_client = openai.AsyncOpenAI(
        base_url="https://models.inference.ai.azure.com", api_key=os.getenv("GITHUB_TOKEN")
    )
    searcher = PostgresSearcher(
        postgres_host=os.environ["POSTGRES_HOST"],
        postgres_username=os.environ["POSTGRES_USERNAME"],
        postgres_database=os.environ["POSTGRES_DATABASE"],
        postgres_password=os.environ.get("POSTGRES_PASSWORD"),
        openai_embed_client=openai_client,
        embed_model="text-embedding-3-small",
        embed_dimensions=256,
    )
    rag_flow = RAGFlow(searcher=searcher, openai_chat_client=openai_client, chat_model="gpt-4o-mini")

    response = await rag_flow.answer(original_user_query=messages[0]["content"], past_messages=messages)
    return response


@app.post("/chat")
async def query(request: QueryRequest):
    try:
        messages = [message.model_dump() for message in request.messages]
        response = await do_rag(messages)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
