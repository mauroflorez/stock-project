"""
Ollama API Integration
Handles all communication with local Ollama instance
"""

import requests
import json
from typing import Dict, Optional
from config import OLLAMA_MODEL, OLLAMA_BASE_URL, MAX_OLLAMA_TOKENS, TEMPERATURE


class OllamaAgent:
    """Base class for all AI agents using Ollama"""
    
    def __init__(self, role: str, system_prompt: str):
        self.role = role
        self.system_prompt = system_prompt
        self.model = OLLAMA_MODEL
        self.base_url = OLLAMA_BASE_URL
        
    def generate(self, prompt: str, max_tokens: int = MAX_OLLAMA_TOKENS) -> str:
        """
        Send prompt to Ollama and get response
        """
        try:
            url = f"{self.base_url}/api/generate"
            
            payload = {
                "model": self.model,
                "prompt": f"{self.system_prompt}\n\nUser Request: {prompt}",
                "stream": False,
                "options": {
                    "temperature": TEMPERATURE,
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(url, json=payload, timeout=300)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except requests.exceptions.ConnectionError:
            raise Exception(
                "Cannot connect to Ollama. Make sure Ollama is running.\n"
                "Start it with: ollama serve"
            )
        except Exception as e:
            raise Exception(f"Error calling Ollama: {str(e)}")
    
    def chat(self, messages: list) -> str:
        """
        Alternative chat-based interface
        """
        try:
            url = f"{self.base_url}/api/chat"
            
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": TEMPERATURE,
                    "num_predict": MAX_OLLAMA_TOKENS
                }
            }
            
            response = requests.post(url, json=payload, timeout=300)
            response.raise_for_status()
            
            result = response.json()
            return result.get("message", {}).get("content", "")
            
        except Exception as e:
            raise Exception(f"Error in chat: {str(e)}")


def check_ollama_status() -> Dict:
    """
    Check if Ollama is running and what models are available
    """
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json()
        
        model_names = [m['name'] for m in models.get('models', [])]
        
        return {
            "running": True,
            "available_models": model_names,
            "configured_model": OLLAMA_MODEL,
            "model_ready": OLLAMA_MODEL in model_names
        }
    except:
        return {
            "running": False,
            "available_models": [],
            "configured_model": OLLAMA_MODEL,
            "model_ready": False
        }


def pull_model(model_name: str = OLLAMA_MODEL) -> bool:
    """
    Pull/download a model if not already available
    """
    try:
        print(f"Pulling model {model_name}... This may take a few minutes.")
        url = f"{OLLAMA_BASE_URL}/api/pull"
        
        payload = {"name": model_name, "stream": True}
        
        response = requests.post(url, json=payload, stream=True, timeout=3600)
        
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "status" in data:
                    print(f"  {data['status']}")
        
        print(f"✓ Model {model_name} ready!")
        return True
        
    except Exception as e:
        print(f"✗ Error pulling model: {str(e)}")
        return False


if __name__ == "__main__":
    # Test Ollama connection
    print("Testing Ollama connection...")
    status = check_ollama_status()
    
    if not status["running"]:
        print("✗ Ollama is not running!")
        print("  Start it with: ollama serve")
    else:
        print("✓ Ollama is running")
        print(f"  Available models: {status['available_models']}")
        
        if not status["model_ready"]:
            print(f"\n✗ Model '{OLLAMA_MODEL}' not found")
            print(f"  Pulling model...")
            pull_model()
        else:
            print(f"✓ Model '{OLLAMA_MODEL}' is ready")
            
            # Test generation
            print("\nTesting generation...")
            agent = OllamaAgent("test", "You are a helpful assistant.")
            response = agent.generate("Say hello in one sentence.")
            print(f"  Response: {response}")
