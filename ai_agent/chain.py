from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from ai_agent.tools import agent_tools

checkpointer = InMemorySaver()

llm = ChatOllama(model="gpt-oss:20b-cloud", host='http://ollama:11434')
#model = deepseek-v3.1:671b-cloud gpt-oss:120b-cloud, gpt-oss:20b-cloud, qwen3-next:80b-cloud ministral-3:8b-cloud ministral-3:3b-cloud "qwen2.5-coder:0.5b"

agent = create_agent(
    model = llm,
    tools = agent_tools,
    system_prompt="Ты виртуальный ассистент компании ВостокТехГаз",
    checkpointer=checkpointer
)


async def chat_chain(user_message: str, user_id: str):
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": user_message}]},
        {"configurable": {"thread_id": user_id}}
    )
    print(response)
    return response.get("messages")[-1].content
