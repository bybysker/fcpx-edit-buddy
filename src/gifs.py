import os 
import json
from dotenv import load_dotenv
from urllib import parse, request

load_dotenv()

def get_n_gifs(query, n=5):
    search_url = "http://api.giphy.com/v1/gifs/search"

    params = parse.urlencode({
      "q": query,
      "api_key": os.getenv("GIPHY_API_KEY"),
      "limit": "5"
    })

    with request.urlopen("".join((search_url, "?", params))) as response:
      data = json.loads(response.read())

    return [ gif['images']['original']['url'] for gif in data['data']]


query = "cat"
gifs_urls = get_n_gifs(query)

gifs_urls