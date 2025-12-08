#!/usr/bin/env python3
"""
Display Server voor Go2 Robot

Toont informatie op een gekoppelde PC/scherm via web interface.
"""

import sys
from pathlib import Path
from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import threading
import time
from typing import Optional, Dict, Any, List
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

app = Flask(__name__)
CORS(app)

# Globale state voor display content
display_content: Dict[str, Any] = {
    "title": "Go2 Robot Display",
    "content": "",
    "type": "text",  # text, search_results, image, video
    "timestamp": None,
    "search_results": [],
    "current_page": "home"
}

# HTML Template voor display
DISPLAY_TEMPLATE = """
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header .subtitle {
            opacity: 0.9;
            font-size: 1.1em;
        }
        
        .content {
            padding: 40px;
            min-height: 400px;
        }
        
        .content-text {
            font-size: 1.3em;
            line-height: 1.8;
            color: #444;
        }
        
        .search-results {
            margin-top: 20px;
        }
        
        .search-result {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .search-result:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .search-result h3 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.4em;
        }
        
        .search-result .url {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
            word-break: break-all;
        }
        
        .search-result .snippet {
            color: #555;
            line-height: 1.6;
        }
        
        .timestamp {
            text-align: center;
            color: #999;
            font-size: 0.9em;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #667eea;
            font-size: 1.2em;
        }
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }
        
        .empty-state h2 {
            font-size: 2em;
            margin-bottom: 10px;
            color: #667eea;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Go2 Robot Display</h1>
            <div class="subtitle">Live informatie van de robot</div>
        </div>
        
        <div class="content">
            {% if type == 'text' %}
                <div class="content-text">{{ content|safe }}</div>
            {% elif type == 'search_results' %}
                <h2 style="margin-bottom: 20px; color: #667eea;">Zoekresultaten</h2>
                <div class="search-results">
                    {% for result in search_results %}
                    <div class="search-result">
                        <h3>{{ result.title }}</h3>
                        <div class="url">{{ result.url }}</div>
                        <div class="snippet">{{ result.snippet }}</div>
                    </div>
                    {% endfor %}
                </div>
            {% else %}
                <div class="empty-state">
                    <h2>Geen content</h2>
                    <p>Wacht op informatie van de robot...</p>
                </div>
            {% endif %}
            
            <div class="timestamp">
                {% if timestamp %}
                Laatste update: {{ timestamp }}
                {% endif %}
            </div>
        </div>
    </div>
    
    <script>
        // Auto-refresh elke 2 seconden
        setInterval(function() {
            fetch('/api/display')
                .then(response => response.json())
                .then(data => {
                    if (data.timestamp !== '{{ timestamp }}') {
                        location.reload();
                    }
                })
                .catch(error => console.error('Error:', error));
        }, 2000);
    </script>
</body>
</html>
"""


@app.route('/')
def display():
    """Hoofdpagina met display content"""
    return render_template_string(
        DISPLAY_TEMPLATE,
        title=display_content.get("title", "Go2 Robot Display"),
        content=display_content.get("content", ""),
        type=display_content.get("type", "text"),
        search_results=display_content.get("search_results", []),
        timestamp=display_content.get("timestamp", "")
    )


@app.route('/api/display', methods=['GET'])
def get_display():
    """Haal huidige display content op"""
    return jsonify(display_content)


@app.route('/api/display', methods=['POST'])
def update_display():
    """Update display content"""
    global display_content
    
    data = request.get_json()
    
    display_content.update({
        "title": data.get("title", display_content.get("title", "Go2 Robot Display")),
        "content": data.get("content", ""),
        "type": data.get("type", "text"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "search_results": data.get("search_results", [])
    })
    
    return jsonify({
        "status": "ok",
        "message": "Display updated",
        "content": display_content
    })


@app.route('/api/display/text', methods=['POST'])
def set_text():
    """Stel tekst in"""
    global display_content
    
    data = request.get_json()
    text = data.get("text", "")
    
    display_content.update({
        "content": text,
        "type": "text",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    return jsonify({"status": "ok", "message": "Text updated"})


@app.route('/api/display/search', methods=['POST'])
def show_search_results():
    """Toon zoekresultaten"""
    global display_content
    
    data = request.get_json()
    query = data.get("query", "")
    results = data.get("results", [])
    
    display_content.update({
        "title": f"Zoekresultaten: {query}",
        "content": f"Zoekopdracht: {query}",
        "type": "search_results",
        "search_results": results,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    return jsonify({"status": "ok", "message": "Search results displayed"})


@app.route('/api/display/clear', methods=['POST'])
def clear_display():
    """Wis display"""
    global display_content
    
    display_content = {
        "title": "Go2 Robot Display",
        "content": "",
        "type": "text",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "search_results": []
    }
    
    return jsonify({"status": "ok", "message": "Display cleared"})


def run_server(host: str = "0.0.0.0", port: int = 5001, debug: bool = False):
    """Start display server"""
    print(f"🚀 Display server starten op http://{host}:{port}")
    print(f"📺 Open in browser: http://localhost:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Go2 Robot Display Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=5001, help="Port (default: 5001)")
    parser.add_argument("--debug", action="store_true", help="Debug mode")
    
    args = parser.parse_args()
    
    run_server(host=args.host, port=args.port, debug=args.debug)

