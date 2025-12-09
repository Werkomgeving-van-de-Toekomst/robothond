#!/usr/bin/env python3
"""
Go2 Audio Streamer

Stream audio van Go2 robot microfoon naar Jetson voor voice processing.
"""

import sys
import os
from pathlib import Path
import argparse
import socket
import struct
import threading
import time

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import pyaudio
    HAS_PYAUDIO = True
except ImportError:
    HAS_PYAUDIO = False
    print("⚠️  pyaudio niet geïnstalleerd. Installeer met: pip install pyaudio")


class Go2AudioStreamer:
    """
    Stream audio van Go2 robot naar Jetson
    """
    
    def __init__(
        self,
        jetson_ip: str = "192.168.123.222",
        port: int = 9999,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 1024
    ):
        """
        Initialiseer Go2 audio streamer
        
        Args:
            jetson_ip: IP adres van Jetson
            port: UDP poort voor audio streaming
            sample_rate: Audio sample rate (16000 voor Whisper)
            channels: Aantal audio kanalen (1 = mono)
            chunk_size: Audio chunk grootte
        """
        self.jetson_ip = jetson_ip
        self.port = port
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        
        self.socket = None
        self.audio_stream = None
        self.is_streaming = False
        self.stream_thread = None
        
        if not HAS_PYAUDIO:
            raise ImportError("pyaudio vereist voor audio streaming")
    
    def start_streaming(self):
        """Start audio streaming naar Jetson"""
        if self.is_streaming:
            print("⚠️  Streaming al actief")
            return
        
        # Maak UDP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Initialiseer PyAudio
        p = pyaudio.PyAudio()
        
        # Open audio input stream
        self.audio_stream = p.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        self.is_streaming = True
        
        def stream_loop():
            print(f"🎤 Start audio streaming naar {self.jetson_ip}:{self.port}")
            try:
                while self.is_streaming:
                    # Lees audio data
                    data = self.audio_stream.read(self.chunk_size, exception_on_overflow=False)
                    
                    # Stuur naar Jetson
                    self.socket.sendto(data, (self.jetson_ip, self.port))
                    
            except Exception as e:
                print(f"❌ Fout bij streaming: {e}")
            finally:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                p.terminate()
                self.socket.close()
        
        self.stream_thread = threading.Thread(target=stream_loop, daemon=True)
        self.stream_thread.start()
        
        print("✓ Audio streaming gestart")
    
    def stop_streaming(self):
        """Stop audio streaming"""
        if not self.is_streaming:
            return
        
        self.is_streaming = False
        
        if self.stream_thread:
            self.stream_thread.join(timeout=2.0)
        
        print("✓ Audio streaming gestopt")
    
    def test_connection(self):
        """Test verbinding met Jetson"""
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            test_socket.settimeout(2)
            
            # Stuur test packet
            test_socket.sendto(b"test", (self.jetson_ip, self.port))
            
            test_socket.close()
            print(f"✓ Test packet verzonden naar {self.jetson_ip}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ Fout bij test: {e}")
            return False


class JetsonAudioReceiver:
    """
    Ontvang audio stream van Go2 robot op Jetson
    """
    
    def __init__(
        self,
        go2_ip: str = "192.168.123.161",
        port: int = 9999,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 1024,
        callback=None
    ):
        """
        Initialiseer audio receiver
        
        Args:
            go2_ip: IP adres van Go2 robot
            port: UDP poort voor audio streaming
            sample_rate: Audio sample rate
            channels: Aantal audio kanalen
            chunk_size: Audio chunk grootte
            callback: Functie die wordt aangeroepen met audio data
        """
        self.go2_ip = go2_ip
        self.port = port
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.callback = callback
        
        self.socket = None
        self.is_receiving = False
        self.receive_thread = None
    
    def start_receiving(self):
        """Start ontvangen van audio stream"""
        if self.is_receiving:
            print("⚠️  Ontvangen al actief")
            return
        
        # Maak UDP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("0.0.0.0", self.port))
        self.socket.settimeout(1.0)
        
        self.is_receiving = True
        
        def receive_loop():
            print(f"🎧 Start ontvangen audio van {self.go2_ip}:{self.port}")
            try:
                while self.is_receiving:
                    try:
                        # Ontvang audio data
                        data, addr = self.socket.recvfrom(self.chunk_size * 2)
                        
                        # Check of van Go2 komt
                        if addr[0] == self.go2_ip:
                            if self.callback:
                                self.callback(data)
                    except socket.timeout:
                        continue
                    except Exception as e:
                        print(f"❌ Fout bij ontvangen: {e}")
                        break
            finally:
                self.socket.close()
        
        self.receive_thread = threading.Thread(target=receive_loop, daemon=True)
        self.receive_thread.start()
        
        print("✓ Audio ontvangen gestart")
    
    def stop_receiving(self):
        """Stop ontvangen van audio stream"""
        if not self.is_receiving:
            return
        
        self.is_receiving = False
        
        if self.receive_thread:
            self.receive_thread.join(timeout=2.0)
        
        print("✓ Audio ontvangen gestopt")


def main():
    parser = argparse.ArgumentParser(
        description="Go2 Audio Streamer - Stream audio van Go2 naar Jetson"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["stream", "receive"],
        required=True,
        help="Mode: 'stream' (op Go2) of 'receive' (op Jetson)"
    )
    parser.add_argument(
        "--jetson-ip",
        type=str,
        default="192.168.123.222",
        help="Jetson IP adres (voor stream mode)"
    )
    parser.add_argument(
        "--go2-ip",
        type=str,
        default="192.168.123.161",
        help="Go2 IP adres (voor receive mode)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9999,
        help="UDP poort voor audio streaming"
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=16000,
        help="Audio sample rate (default: 16000)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "stream":
        # Stream mode: Op Go2 robot
        print("=" * 70)
        print("  Go2 Audio Streamer - Stream Mode")
        print("=" * 70)
        print(f"\nStream audio naar Jetson: {args.jetson_ip}:{args.port}")
        print(f"Sample rate: {args.sample_rate} Hz")
        print("\nDruk Ctrl+C om te stoppen\n")
        
        streamer = Go2AudioStreamer(
            jetson_ip=args.jetson_ip,
            port=args.port,
            sample_rate=args.sample_rate
        )
        
        # Test verbinding
        if not streamer.test_connection():
            print("⚠️  Kon geen verbinding maken met Jetson")
            return 1
        
        try:
            streamer.start_streaming()
            
            # Wacht tot gestopt
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n⚠️  Gestopt door gebruiker")
        finally:
            streamer.stop_streaming()
    
    elif args.mode == "receive":
        # Receive mode: Op Jetson
        print("=" * 70)
        print("  Go2 Audio Receiver - Receive Mode")
        print("=" * 70)
        print(f"\nOntvang audio van Go2: {args.go2_ip}:{args.port}")
        print(f"Sample rate: {args.sample_rate} Hz")
        print("\nDruk Ctrl+C om te stoppen\n")
        
        def audio_callback(data):
            """Callback voor ontvangen audio"""
            # Hier kun je audio verwerken voor voice recognition
            # Bijvoorbeeld: stuur naar voice controller
            print(f"📦 Ontvangen {len(data)} bytes audio")
        
        receiver = JetsonAudioReceiver(
            go2_ip=args.go2_ip,
            port=args.port,
            sample_rate=args.sample_rate,
            callback=audio_callback
        )
        
        try:
            receiver.start_receiving()
            
            # Wacht tot gestopt
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n⚠️  Gestopt door gebruiker")
        finally:
            receiver.stop_receiving()
    
    return 0


if __name__ == "__main__":
    exit(main())

