from langgraph.graph import StateGraph, START, MessagesState
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.messages.utils import trim_messages, count_tokens_approximately
from ai_agent.chain import agent


class AgentState(MessagesState):
    user_id: str

async def router_node(state: AgentState):
    messages = trim_messages(
        state["messages"],
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=128,  # Максимальное количество токенов после обрезки
        start_on="human",
        end_on=("human", "tool"),
    )
    user_message = messages[-1].content
    user_id = state["user_id"]

    result = await agent.ainvoke({"messages": [{"role": "user", "content": user_message}]},
        {"configurable": {"thread_id": user_id}})
    
        
    if isinstance(result, dict) and "messages" in result:
        new_messages = result["messages"]
    else:
        new_messages = messages + [AIMessage(content=str(result))]
 
    state["messages"] = new_messages
    print(state)
    return state

graph = StateGraph(AgentState)

graph.add_node("router", router_node)

graph.add_edge(START, "router")

checkpointer = InMemorySaver()
app = graph.compile(checkpointer=checkpointer)


async def chat_chain_graph(user_message: str, user_id: str, user_name: str):
    
    message = f'Сообщение от клиента {user_name} user_id: {user_id}\n{user_message}'
    state = AgentState(
    user_id=user_id,
    messages=[HumanMessage(content=message)]
    )
    result = await app.ainvoke(state, {"configurable": {"thread_id": user_id}})
    last_message = result["messages"][-1].content
    return last_message
