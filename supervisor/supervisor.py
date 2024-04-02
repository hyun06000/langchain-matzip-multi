from tools.conversation_tool import (
    conversation_tool_with_blog_expert,
    conversation_tool_with_map_expert,
    conversation_tool_with_translation_expert,
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
        StructuredTool.from_function(conversation_tool_with_blog_expert),
        StructuredTool.from_function(conversation_tool_with_map_expert),
        StructuredTool.from_function(conversation_tool_with_translation_expert),
    ]
    tool_names = [tool.name for tool in tools]

    prompt = CustomPromptTemplate(
        template=ENG_TEMPLATE,
        tools=tools,
        input_variables=["input", "intermediate_steps", "chat_history"]
    )
    
    llm = ChatOpenAI(temperature=0, model="gpt-4")
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    
    agent = LLMSingleActionAgent(
        llm_chain=llm_chain,
        output_parser=JSONAgentOutputParser(),
        stop=["\nObservation:"],
        allowed_tools=tool_names
    )

    memory = ConversationBufferWindowMemory(k=8, memory_key="chat_history")
    

    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=memory,
        max_iterations=64,
        handle_parsing_errors=True
    )
    prompt = input("Type your prompt here:\n")
    agent_executor.run(ENG_PURPOSE.format(query=prompt))

if __name__ == "__main__":
    main()