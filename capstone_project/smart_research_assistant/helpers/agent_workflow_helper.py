from langchain.schema import HumanMessage
from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from smart_research_assistant.types.agents.agent_state import AgentState
from streamlit.delta_generator import DeltaGenerator


def update_state(message: BaseMessage, state: AgentState, log: DeltaGenerator) -> AgentState:
    state["messages"].append(message)
    colored_messages = []
    for message in state["messages"]:
        colored_messages.append(color_message(message))

    log.write("\n\n".join(colored_messages))
    return state


def color_message(message: BaseMessage) -> str:
    if isinstance(message, SystemMessage):
        return f":violet-badge[SYSTEM:  {str(message.content)}]"
    if isinstance(message, AIMessage):
        return f":blue-badge[AI:  {str(message.content)}]"
    if isinstance(message, HumanMessage):
        return f":green-badge[HUMAN:  {str(message.content)}]"

    return str(message.content)
