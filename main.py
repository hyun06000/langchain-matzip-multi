from tools.tools import (
    terminal_tool,
    search_url_tool,
    request_url_tool,
    readfile_tool,
    savefile_tool,
)
from langchain.tools import StructuredTool
from prompts.template import ENG_TEMPLATE
from prompts.purpose import ENG_PURPOSE
from utils.customization import CustomPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.agents import LLMSingleActionAgent
from langchain.agents.output_parsers import JSONAgentOutputParser
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import AgentExecutor


from dotenv import load_dotenv
load_dotenv()



def main():
    
    tools = [
        StructuredTool.from_function(terminal_tool),
        StructuredTool.from_function(search_url_tool),
        StructuredTool.from_function(request_url_tool),
        StructuredTool.from_function(savefile_tool),
        StructuredTool.from_function(readfile_tool),
        StructuredTool.from_function(request_url_tool),
    ]
    tool_names = [tool.name for tool in tools]

    prompt = CustomPromptTemplate(
        template=ENG_TEMPLATE,
        tools=tools,
        input_variables=["input", "intermediate_steps"]
    )
    
    llm = ChatOpenAI(temperature=0, model="gpt-4-1106-preview")
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    
    agent = LLMSingleActionAgent(
        llm_chain=llm_chain,
        output_parser=JSONAgentOutputParser(),
        stop=["\nObservation:"],
        allowed_tools=tool_names
    )

    memory = ConversationBufferWindowMemory(k=8)
    

    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=memory,
        max_iterations=64,
        handle_parsing_errors=True
    )
    
    agent_executor.run(ENG_PURPOSE)