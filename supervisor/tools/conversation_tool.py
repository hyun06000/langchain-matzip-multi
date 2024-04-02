import requests

def conversation_tool_with_blog_expert(prompt: str) -> str:
    """With this tool, you can make conversation with blog expert chatbot.
    He can give a high quality information from blogs on world wide web."""
    try:
        response = requests.post(
            "http://localhost:8001/prompt",
            json={"text":f"{prompt}"}
        )
        return response.text
    except Exception as e:
        return "Something went wrong. Please try again"


def conversation_tool_with_map_expert(prompt: str) -> str:
    """With this tool, you can make conversation with map expert chatbot.
    He can give a high quality map information from google place search."""
    try:
        response = requests.post(
            "http://localhost:8002/prompt",
            json={"text":f"{prompt}"}
        )
        return response.text
    except Exception as e:
        return "Something went wrong. Please try again"


def conversation_tool_with_translation_expert(prompt: str) -> str:
    """With this tool, you can make conversation with translation expert chatbot.
    He can give a high quality translation from English to Korean."""
    try:
        response = requests.post(
            "http://localhost:8003/prompt",
            json={"text":f"{prompt}"}
        )
        return response.text
    except Exception as e:
        return "Something went wrong. Please try again"
