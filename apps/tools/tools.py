import os
import io
import subprocess
from dotenv import load_dotenv
from serpapi import GoogleSearch
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

from bs4 import BeautifulSoup
import requests
import re
from PyPDF2 import PdfReader

load_dotenv()

def google_place_search_tool(place_name: str) -> str:
    """Google place search tool. The input string should be a name of place. This tool give you place name, address, price level,
    rating from other people, and user rating count.
    """
    GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']
    feild_mask = ",".join(
        [
            "places.displayName",
            "places.formattedAddress",
            "places.priceLevel",
            "places.rating",
            "places.userRatingCount",
            
        ]
    )

    command = (
        f"""curl -X POST -d '{{"textQuery" : "{place_name}", "minRating": 4.0, "openNow": true, "maxResultCount": 5}}' """
        f"""-H 'Content-Type: application/json' """
        f"""-H 'X-Goog-Api-Key: {GOOGLE_API_KEY}' """
        f"""-H 'X-Goog-FieldMask: {feild_mask}' """
        """'https://places.googleapis.com/v1/places:searchText'"""
    )

    process = subprocess.Popen(
                [f"""{command}"""],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )
    stdout = process.stdout.read().decode("UTF-8")
    return stdout


def search_url_tool(text: str) -> str:
    """google search tool to get url related to the keywords"""
    params = {
        "q": text,
        "num": 5,
        "api_key": os.environ["SERPAPI_API_KEY"],
        "google_domain": "google.co.kr",
    }
    
    
    try:
        search = GoogleSearch(params)
        search_dict = search.get_dict()
        
        if "organic_results" not in search_dict:
            return "There is no result. Please change the search phrase to a more shorter and generic words."
        
        res = list(map(
            lambda x: f"TITLE: {x['title']} | LINK: {x['link']} | DESCRIPTION: {x['snippet']}",
            search.get_dict()["organic_results"]
        ))
    except Exception as e:
        res = str(e)
    
    return res

def savefile_tool(file_name, file_contents:str) -> str:
    """Save (append) script as a file with file name and file contents which is a code.
    This tool need two inputs like {action_input: {file_name:str , file_contents:str}}.
    """
    
    try:
        with open(file_name, 'w+') as f:
            f.write(file_contents + "\n")

        return f"file saved : {file_name}"
    except Exception as e:
        return f"Error: {e}"


def readfile_tool(file_name: str) -> str:
    """Read script as a file with file name and file contents which is a code"""

    try:
        with open(file_name, "r+") as f:
            file_contents = f.read()

        return f"file_contents : {file_contents}"
    except Exception as e:
        return f"Error: {e}"


def article_summary_tool(news_url: str) -> str:
    """This tool is for web news article summarizer.
    If you input a url pointing to news article,
    this tool will give you a paragraph of summary of the news.
    """

    try:
        try:
            response = requests.get(news_url, verify=False)
            if news_url.endswith(".pdf"):
                text = ""
                with io.BytesIO(response.content) as f:
                    pdf = PdfReader(f)
                    for page_num in range(len(pdf.pages)):
                        text += pdf.pages[page_num].extract_text() + '\n'
            else:
                soup = BeautifulSoup(response.text, "html.parser")
                text = soup.body.get_text().strip().encode('utf8','replace').decode()
            text = re.sub(r"\n"," ",text)
            text = re.sub(r"\s+"," ",text)
        except Exception as e:
            text = "Something went wrong. Please try again with another URL"
        
        prompt = PromptTemplate.from_template("""
            You are a journalist.
            Could you give me the summary of the only article part of this paragraph?
            Paragraph can be written in a mixture between local language and English.
            
            ```paragraph
            {paragraph}
            ```
            
            Summary:
        """)
        runnable = prompt | ChatOpenAI(temperature=0, model="gpt-4")
        summary = runnable.invoke({"paragraph": text[:5000]})
                
        return f"Summary : {summary}"
    except Exception as e:
        return f"Error: {e}"


def request_url_tool(input_url: str) -> str:
    """With this tool, you can get the contents in the page of url and pdf link."""
    try:
        response = requests.get(input_url, verify=False, timeout=1)
        if input_url.endswith(".pdf"):
            text = ""
            with io.BytesIO(response.content) as f:
                pdf = PdfReader(f)
                for page_num in range(len(pdf.pages)):
                    text += pdf.pages[page_num].extract_text() + '\n'
        else:
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.body.get_text().strip()
        text = re.sub(r"\n"," ",text)
        text = re.sub(r"\s+"," ",text)
        return text [:2500]
    except Exception as e:
        return "Something went wrong. Please try again with another URL"

def translation_tool(asking: str) -> str:
    """ask translation to ChatGPT.
    You should make prompt like : what is the "..." in <language>?
    For example, what is the "hello my friend!" in spenish?
    """

    try:
        prompt = PromptTemplate.from_template("You are a translator. Please give me the translation. {asking}")
        runnable = prompt | ChatOpenAI(temperature=0, model="gpt-4")
        thinking = runnable.invoke({"asking": asking})
        
        
        return f"Thinking : {thinking}"
    except Exception as e:
        return f"Error: {e}"

