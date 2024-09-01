import re
from urllib.parse import urlparse, parse_qs
import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
import json

def get_youtube_video_id(url):
    # Extract video ID from various YouTube URL formats
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
        if parsed_url.path[:7] == '/embed/':
            return parsed_url.path.split('/')[2]
        if parsed_url.path[:3] == '/v/':
            return parsed_url.path.split('/')[2]
    return None

def get_youtube_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return ' '.join([entry['text'] for entry in transcript])
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None

def scrape_web_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract text from p tags (customize as needed)
        paragraphs = soup.find_all('p')
        content = ' '.join([p.get_text() for p in paragraphs])
        return content
    except Exception as e:
        print(f"Error scraping content: {e}")
        return None

def query_ollama(content, query):
    url = "http://localhost:11434/api/generate"
    
    prompt = f"""Context: {content}

Question: {query}

Please provide a concise answer based on the given context."""

    payload = {
        "model": "qwen2:1.5b",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        return result['response']
    except requests.exceptions.RequestException as e:
        print(f"Error querying Ollama: {e}")
        return None

def save_query_history(url, query, answer):
    history = load_previous_queries(url)
    history.append({"query": query, "answer": answer})
    with open(f"{url.replace('/', '_')}_history.json", 'w') as f:
        json.dump(history, f)

def load_previous_queries(url):
    try:
        with open(f"{url.replace('/', '_')}_history.json", 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
