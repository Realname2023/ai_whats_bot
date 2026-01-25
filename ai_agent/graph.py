from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage, AIMessage
from ai_agent.chain import agent
from data_base.anotations import AgentState


async def router_node(state: AgentState):
    user_message = state.messages[-1].content
    user_id = state.user_id

    result = await agent.ainvoke({"messages": [{"role": "user", "content": user_message}]},
        {"configurable": {"thread_id": user_id}})
    
        
    if isinstance(result, dict) and "messages" in result:
        new_messages = result["messages"]
    else:
        new_messages = state.messages + [AIMessage(content=str(result))]
    answer = {
        **state.model_dump(),
        "messages": new_messages
    }

    print(answer)

    return answer

graph = StateGraph(AgentState)

graph.add_node("router", router_node)

graph.set_entry_point("router")

checkpointer = InMemorySaver()
app = graph.compile(checkpointer=checkpointer)


async def chat_chain_graph(user_message: str, user_id: str):
    
    message = f'Сообщение от клиента user_id: {user_id}\n{user_message}'
    state = AgentState(
    user_id=user_id,
    messages=[HumanMessage(content=message)]
    )
    result = await app.ainvoke(state, {"configurable": {"thread_id": user_id}})
    last_message = result["messages"][-1].content
    return last_message
