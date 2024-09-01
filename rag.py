from flask import Flask, render_template, request, jsonify
from flask_cors import CORS  # Add this import
# Import your existing functions here
from utils import get_youtube_video_id, get_youtube_transcript, scrape_web_content, query_ollama, save_query_history, load_previous_queries

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/load_content', methods=['POST'])
def load_content():
    url = request.json['url']
    if 'youtube.com' in url or 'youtu.be' in url:
        video_id = get_youtube_video_id(url)
        if video_id:
            content = get_youtube_transcript(video_id)
        else:
            return jsonify({"error": "Invalid YouTube URL"}), 400
    else:
        content = scrape_web_content(url)
    
    if not content:
        return jsonify({"error": "Failed to extract content"}), 400
    
    return jsonify({"message": f"Content loaded from: {url}", "content": content})

@app.route('/ask_question', methods=['POST'])
def ask_question():
    content = request.json['content']
    query = request.json['query']
    url = request.json['url']
    
    answer = query_ollama(content, query)
    if answer:
        save_query_history(url, query, answer)
        return jsonify({"answer": answer})
    else:
        return jsonify({"error": "Failed to get an answer"}), 500

@app.route('/get_history', methods=['POST'])
def get_history():
    url = request.json['url']
    history = load_previous_queries(url)
    return jsonify({"history": history})

if __name__ == '__main__':
    app.run(debug=True)