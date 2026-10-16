"""app.py — Chainlit UI entrypoint for the Meridian Wealth Financial Analyst agent.

This is the only new code in the project: it receives a chat message from the Chainlit UI,
invokes the notebook's agent exactly as the notebook does, and shows the final answer.

Run from inside financial_agent_app/:
    chainlit run app.py -w
"""
import chainlit as cl

from agent import agent


@cl.on_chat_start
async def start_chat():
    """Greet the user when a new chat session opens."""
    await cl.Message(
        content=(
            "👋 Hi, I'm the Meridian Wealth Partners financial analyst agent.\n\n"
            "Ask me for a client briefing (e.g. CLT-001), a sector comparison, "
            "a policy-compliance check, or the latest market news."
        )
    ).send()


@cl.on_message
async def handle_message(user_message: cl.Message):
    """Send the user's message to the agent and display its final answer."""
    # agent.invoke is synchronous, so run it in a worker thread to keep the UI responsive.
    agent_result = await cl.make_async(agent.invoke)(
        {
            "messages": [
                {"role": "user", "content": user_message.content}
            ]
        }
    )

    final_message = agent_result["messages"][-1]
    answer_text = final_message.content if hasattr(final_message, "content") else final_message
    await cl.Message(content=str(answer_text)).send()