import os
from pathlib import Path

import chainlit as cl
from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAIError

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set(
        "messages",
        [{"role": "system", "content": "You are a helpful, concise assistant."}],
    )
    await cl.Message(content="Hi! What can I help you with?").send()


@cl.on_message
async def on_message(message: cl.Message):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        await cl.Message(
            content="OPENAI_API_KEY is not set. Add it to the project root .env file and restart Chainlit."
        ).send()
        return

    messages = cl.user_session.get("messages")
    messages.append({"role": "user", "content": message.content})

    try:
        client = AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model=os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4o-mini"),
            messages=messages,
        )
    except OpenAIError:
        messages.pop()
        await cl.Message(
            content="The OpenAI request failed. Check your API key and connection, then try again."
        ).send()
        return

    reply = response.choices[0].message.content or "I couldn't generate a response."
    messages.append({"role": "assistant", "content": reply})
    cl.user_session.set("messages", messages)
    await cl.Message(content=reply).send()
