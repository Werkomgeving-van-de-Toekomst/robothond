#!/usr/bin/env python3
"""
Multi-Jetson Load Balancer

Verdeel voice processing workload over meerdere Jetson servers.
"""

import sys
import os
from pathlib import Path
import argparse
import requests
import random
import time
from typing import List, Dict, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class MultiJetsonLoadBalancer:
    """
    Load balancer voor meerdere Jetson voice servers
    """
    
    def __init__(
        self,
        jetson_servers: List[str],
        strategy: str = "round-robin",
        health_check_interval: int = 5
    ):
        """
        Initialiseer load balancer
        
        Args:
            jetson_servers: Lijst van Jetson server URLs
            strategy: Load balancing strategie (round-robin, random, least-connections)
            health_check_interval: Interval voor health checks (seconden)
        """
        self.jetson_servers = jetson_servers
        self.strategy = strategy
        self.health_check_interval = health_check_interval
        
        self.current_server = 0
        self.server_stats: Dict[str, Dict] = {}
        
        # Initialize stats
        for server in jetson_servers:
            self.server_stats[server] = {
                "requests": 0,
                "errors": 0,
                "last_check": None,
                "status": "unknown"
            }
        
        # Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        self.setup_routes()
        
        # Start health check thread
        self.health_check_thread = None
        self.is_running = False
    
    def get_next_server(self) -> Optional[str]:
        """Kies volgende server gebaseerd op strategie"""
        available_servers = [s for s in self.jetson_servers if self.server_stats[s]["status"] == "online"]
        
        if not available_servers:
            return None
        
        if self.strategy == "round-robin":
            server = available_servers[self.current_server % len(available_servers)]
            self.current_server = (self.current_server + 1) % len(available_servers)
            return server
        
        elif self.strategy == "random":
            return random.choice(available_servers)
        
        elif self.strategy == "least-connections":
            # Kies server met minste requests
            return min(available_servers, key=lambda s: self.server_stats[s]["requests"])
        
        else:
            return available_servers[0]
    
    def check_server_health(self, server: str) -> bool:
        """Check health van één server"""
        try:
            response = requests.get(f"{server}/health", timeout=2)
            if response.status_code == 200:
                self.server_stats[server]["status"] = "online"
                self.server_stats[server]["last_check"] = time.time()
                return True
        except:
            pass
        
        self.server_stats[server]["status"] = "offline"
        self.server_stats[server]["last_check"] = time.time()
        return False
    
    def health_check_loop(self):
        """Continue health check loop"""
        while self.is_running:
            for server in self.jetson_servers:
                self.check_server_health(server)
            time.sleep(self.health_check_interval)
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check voor load balancer en alle Jetsons"""
            jetson_status = {}
            for server in self.jetson_servers:
                jetson_status[server] = {
                    "status": self.server_stats[server]["status"],
                    "requests": self.server_stats[server]["requests"],
                    "errors": self.server_stats[server]["errors"]
                }
            
            return jsonify({
                "status": "ok",
                "strategy": self.strategy,
                "jetsons": jetson_status
            })
        
        @self.app.route('/api/voice/listen', methods=['POST'])
        def forward_voice_command():
            """Forward voice commando naar beschikbare Jetson"""
            server = self.get_next_server()
            
            if not server:
                return jsonify({
                    "status": "error",
                    "message": "Geen beschikbare Jetson servers"
                }), 503
            
            try:
                # Update stats
                self.server_stats[server]["requests"] += 1
                
                # Forward request
                response = requests.post(
                    f"{server}/api/voice/listen",
                    json=request.get_json(),
                    timeout=10
                )
                
                return jsonify(response.json()), response.status_code
                
            except Exception as e:
                self.server_stats[server]["errors"] += 1
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @self.app.route('/api/voice/start', methods=['POST'])
        def start_listening():
            """Start luisteren op alle Jetsons"""
            results = {}
            for server in self.jetson_servers:
                if self.server_stats[server]["status"] == "online":
                    try:
                        response = requests.post(f"{server}/api/voice/start", timeout=2)
                        results[server] = "ok" if response.status_code == 200 else "error"
                    except:
                        results[server] = "error"
                else:
                    results[server] = "offline"
            
            return jsonify({
                "status": "ok",
                "results": results
            })
        
        @self.app.route('/api/voice/stop', methods=['POST'])
        def stop_listening():
            """Stop luisteren op alle Jetsons"""
            results = {}
            for server in self.jetson_servers:
                if self.server_stats[server]["status"] == "online":
                    try:
                        response = requests.post(f"{server}/api/voice/stop", timeout=2)
                        results[server] = "ok" if response.status_code == 200 else "error"
                    except:
                        results[server] = "error"
                else:
                    results[server] = "offline"
            
            return jsonify({
                "status": "ok",
                "results": results
            })
        
        @self.app.route('/api/stats', methods=['GET'])
        def get_stats():
            """Get statistieken van alle servers"""
            return jsonify({
                "status": "ok",
                "strategy": self.strategy,
                "servers": self.server_stats
            })
    
    def run(self, host: str = "0.0.0.0", port: int = 8889, debug: bool = False):
        """Start load balancer"""
        self.is_running = True
        
        # Start health check thread
        import threading
        self.health_check_thread = threading.Thread(target=self.health_check_loop, daemon=True)
        self.health_check_thread.start()
        
        print("=" * 70)
        print("  Multi-Jetson Load Balancer")
        print("=" * 70)
        print(f"\nJetson servers: {self.jetson_servers}")
        print(f"Strategy: {self.strategy}")
        print(f"Health check interval: {self.health_check_interval}s")
        print(f"\nStart load balancer op http://{host}:{port}")
        print("\nDruk Ctrl+C om te stoppen\n")
        
        self.app.run(host=host, port=port, debug=debug, threaded=True)
    
    def shutdown(self):
        """Stop load balancer"""
        self.is_running = False
        if self.health_check_thread:
            self.health_check_thread.join(timeout=2.0)


def main():
    parser = argparse.ArgumentParser(
        description="Multi-Jetson Load Balancer"
    )
    parser.add_argument(
        "--jetson-servers",
        type=str,
        nargs="+",
        required=True,
        help="Jetson server URLs (bijv. http://192.168.1.100:8888 http://192.168.1.101:8888)"
    )
    parser.add_argument(
        "--strategy",
        type=str,
        default="round-robin",
        choices=["round-robin", "random", "least-connections"],
        help="Load balancing strategie (default: round-robin)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8889,
        help="Load balancer poort (default: 8889)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Load balancer host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--health-check-interval",
        type=int,
        default=5,
        help="Health check interval in seconden (default: 5)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Debug mode"
    )
    
    args = parser.parse_args()
    
    try:
        load_balancer = MultiJetsonLoadBalancer(
            jetson_servers=args.jetson_servers,
            strategy=args.strategy,
            health_check_interval=args.health_check_interval
        )
        
        load_balancer.run(host=args.host, port=args.port, debug=args.debug)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Gestopt door gebruiker")
    except Exception as e:
        print(f"\n❌ Fout: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        if 'load_balancer' in locals():
            load_balancer.shutdown()
    
    return 0


if __name__ == "__main__":
    exit(main())

