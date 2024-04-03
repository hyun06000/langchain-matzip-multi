from fastapi import FastAPI
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory


from dotenv import load_dotenv
load_dotenv()


app = FastAPI()


llm = ChatOpenAI(temperature=0, model="gpt-4")
template = """You are a nice chatbot having a conversation with a human.
You are expert at translation between English and Korean.
If the input is Korean, you shuold translate it as English.
If The input is English, you should translate it as Korean.
No need to answer for the input.
just translate it.

Previous conversation:
{chat_history}

New human sentence: {question}
Translation:"""
prompt = PromptTemplate.from_template(template)
memory = ConversationBufferMemory(memory_key="chat_history")
conversation = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=True,
    memory=memory
)


from pydantic import BaseModel
class Item(BaseModel):
    text: str = None


@app.post("/prompt/")
async def read_root(message:Item):
    
    ai_answer = conversation({"question": f"{message.text}"})

    return {"ai_answer": ai_answer}
