from pydantic import BaseModel
from fastapi import FastAPI
from langchain.chat_models import ChatOpenAI
from langchain.agents import LLMSingleActionAgent
from langchain.agents.output_parsers import JSONAgentOutputParser
from langchain.tools import StructuredTool
from langchain.agents import AgentExecutor
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferWindowMemory

from dotenv import load_dotenv
load_dotenv()

from tools.tools import (
    search_url_tool,
    request_url_tool,
)
from utils.customization import CustomPromptTemplate
from prompts.blog_expert.template import KOR_TEMPLATE



app = FastAPI()

tools = [
    StructuredTool.from_function(search_url_tool),
    StructuredTool.from_function(request_url_tool),
]
tool_names = [tool.name for tool in tools]

prompt = CustomPromptTemplate(
    template=KOR_TEMPLATE,
    tools=tools,
    input_variables=["input", "intermediate_steps", "chat_history"]
)

llm = ChatOpenAI(temperature=0, model="gpt-4")
llm_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=True
)
agent = LLMSingleActionAgent(
    llm_chain=llm_chain,
    output_parser=JSONAgentOutputParser(),
    stop=["\nObservation:", "\n- 관측"],
    allowed_tools=tool_names,
    return_intermediate_steps=True,
)
memory = ConversationBufferWindowMemory(k=4, memory_key="chat_history")
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
    memory=memory,
    handle_parsing_errors=True,    
)

class Item(BaseModel):
    text: str = None

@app.post("/prompt/")
async def read_root(message:Item):
    
    ai_answer = agent_executor.run({"input": f"{message.text}"},)

    return {"ai_answer": ai_answer}
