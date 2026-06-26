from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import create_react_agent, AgentExecutor
from dental_agent.config.settings import GROQ_API_KEY, MODEL_NAME,TEMPERATURE

llm = ChatGroq(api_key=GROQ_API_KEY, model_name=MODEL_NAME, temperature=TEMPERATURE)

system_prompt = """You are a dental clinic assistant AI. 
Your job is to help patients book appointments and provide general information.

You can: 
- Answer questions about clinic services
- Check doctor availability
- Schedule/Cancel/Reschedule appointments

Respond in a friendly, professional, and clear manner. 

If you don't have enough information, ask clarifying questions.
"""

agent_executor = create_react_agent(llm, [system_prompt])