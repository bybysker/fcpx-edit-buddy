import os 
import json
from dotenv import load_dotenv
from urllib import parse, request
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

## From a srt file, define the main themes of a videos and give as output a list of keywords
## to be used for a search on gifs

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Keywords(BaseModel):
    keywords: list[str]

def get_main_themes(srt_file):
   print(f"Extracting main themes from SRT file: {srt_file}")
   prompt = f"""
   You are an expert in video editing.
   You are given a srt file of a video.
   Your task is to extract the main themes of the video and give as output a list of keywords
   to be used for a search on gifs.
   Max keywords: 5
   if error, return "[]".
   """
   transcript = open(srt_file, "r").read()
   print(f"Loaded transcript of length: {len(transcript)}")
  
   print("Sending request to OpenAI API...")
   response = client.beta.chat.completions.parse(
      model="gpt-4o-2024-08-06",
      messages=[{"role": "system", "content": prompt}, {"role": "user", "content": transcript}],
      response_format=Keywords,
      seed=42
   )
   keywords = response.choices[0].message.parsed
   print(f"Received keywords from OpenAI: {keywords}")
   return keywords
   

def get_n_gifs(query, n=5):
    print(f"Searching for {n} gifs with query: {query}")
    search_url = "http://api.giphy.com/v1/gifs/search"

    params = parse.urlencode({
      "q": query,
      "api_key": os.getenv("GIPHY_API_KEY"),
      "limit": "5"
    })

    print("Sending request to Giphy API...")
    with request.urlopen("".join((search_url, "?", params))) as response:
      data = json.loads(response.read())

    gif_urls = [gif['images']['original']['url'] for gif in data['data']]
    print(f"Retrieved {len(gif_urls)} gifs from Giphy")
    print(f"Gif URLs: {gif_urls}")

    return gif_urls

def download_gif(url, name, folder):
    """
    Downloads a GIF from the provided URL and saves it to the specified folder.
    """
    print(f"Downloading gif from URL: {url}")
    if not os.path.exists(folder):
        print(f"Creating folder: {folder}")
        os.makedirs(folder)
    
    gif_name = name + ".gif"
    file_path = os.path.join(folder, gif_name)
    print(f"Saving gif to: {file_path}")
    
    with request.urlopen(url) as response, open(file_path, 'wb') as out_file:
        gif_data = response.read()
        out_file.write(gif_data)
        print(f"Successfully downloaded and saved gif ({len(gif_data)} bytes)")


def download_gifs(srt_file, folder="gifs"):
    print(f"\nStarting gif download process for SRT file: {srt_file}")
    keywords = get_main_themes(srt_file)
    print(f"\nProcessing keywords: {keywords}")
    for keyword in keywords.keywords:
        print(f"\nProcessing keyword: {keyword}")
        gifs_urls = get_n_gifs(keyword)
        for i, url in enumerate(gifs_urls):
            download_gif(url, keyword + f"_{i}", folder)

