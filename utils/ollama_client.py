"""
Ollama Client - Handles all communication with local Ollama instance
"""

import requests
import json
from typing import Optional, Dict, Any
from config import OLLAMA_BASE_URL, OLLAMA_MODEL, MAX_TOKENS, TEMPERATURE


class OllamaClient:
    """Client for interacting with local Ollama instance"""
    
    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = OLLAMA_MODEL):
        self.base_url = base_url
        self.model = model
        self.endpoint = f"{base_url}/api/generate"
        
    def is_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Ollama not available: {e}")
            return False
    
    def generate(self, 
                 prompt: str, 
                 system_prompt: Optional[str] = None,
                 temperature: float = TEMPERATURE,
                 max_tokens: int = MAX_TOKENS) -> str:
        """
        Generate a response from Ollama
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system instructions for the agent
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        
        # Combine system prompt and user prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            response = requests.post(self.endpoint, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error calling Ollama: {e}")
            return f"Error: Could not generate response - {str(e)}"
    
    def list_models(self) -> list:
        """List available models in Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            return []
        except Exception as e:
            print(f"Error listing models: {e}")
            return []


# Convenience function
def call_ollama(prompt: str, system_prompt: str = None) -> str:
    """Quick wrapper to call Ollama with a prompt"""
    client = OllamaClient()
    return client.generate(prompt, system_prompt)


if __name__ == "__main__":
    # Test the Ollama connection
    client = OllamaClient()
    
    print("🔍 Checking Ollama status...")
    if client.is_available():
        print("✅ Ollama is running!")
        print(f"📦 Using model: {client.model}")
        
        models = client.list_models()
        if models:
            print(f"📋 Available models: {', '.join(models)}")
        
        # Test generation
        print("\n🧪 Testing generation...")
        response = client.generate("Say hello in one sentence.")
        print(f"Response: {response}")
    else:
        print("❌ Ollama is not running. Please start it with: ollama serve")
