from fastapi import FastAPI
from langchain.chat_models import ChatOpenAI
from langchain.agents import LLMSingleActionAgent
from langchain.agents.output_parsers import JSONAgentOutputParser
from langchain.tools import StructuredTool
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import AgentExecutor
from langchain.chains import LLMChain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory


from dotenv import load_dotenv
load_dotenv()

from tools.tools import google_place_search_tool
from utils.customization import CustomPromptTemplate




app = FastAPI()
message_history = ChatMessageHistory()
context_memory = ConversationBufferWindowMemory(k=4)
memory = ConversationBufferWindowMemory(k=4, memory_key="chat_history", input_key="input")
template = """
You are a nice chatbot having conversation with human.
You are an expert to suggest a place from google place search.
You can search a place from goole place search.
You can understand all the results from the search tool.
You can explane why you suggest the place in nice and warm sentence.

These are the set of tools you can use. 
If you think it is a proper tool to solve your problem, whatever you can use. 

tools:
{tools}

Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).
Valid "action" values: "Final Answer" or {tool_names}
Provide only ONE action per $JSON_BLOB, as shown:
```
{{
  "action": $TOOL_NAME,
  "action_input": $INPUT
}}
```
Please follow the input schema of tools.

You MUST follow this answering template.
Your answer must be in this shape.

New human prompt: The new question or query from human.
WhatYouDid: what you did in the just previous step.
Planing: Make a plan what will you do based on the previous step. Each plan has a simple task. Anyone should be able to achieve the purpose if they follow your plan.
Understanding: Understand the 'Observation' or 'Purpose' from previous step.
ThisStep: Write a simple task for just this step.
Action:
```
$JSON_BLOB
```
Observation: this is the result of the action.
Understanding: Your understanding for the observation.
Action:
```
{{
  "action": "Final Answer",
  "action_input": "Final response to human"
}}
```

Previous conversation: {chat_history}

New human prompt: {input}
WhatYouDid: {agent_scratchpad}
Planing: """

tools = [
    StructuredTool.from_function(google_place_search_tool),
]
tool_names = [tool.name for tool in tools]

prompt = CustomPromptTemplate(
    template=template,
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
    stop=["\nObservation:"],
    allowed_tools=tool_names,
    return_intermediate_steps=True,
)
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
    memory=memory,
    handle_parsing_errors=True,
    
)

from pydantic import BaseModel
class Item(BaseModel):
    text: str = None

@app.post("/prompt/")
async def read_root(message:Item):
    
    ai_answer = agent_executor.run({"input": f"{message.text}"},)

    return {"ai_answer": ai_answer}
