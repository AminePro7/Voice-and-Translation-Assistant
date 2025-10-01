#!/usr/bin/env python3
"""
Test script for Ollama with Gemma 3:1b model
This script tests the Ollama installation and Gemma 3:1b model functionality.
"""

import sys
import time
import json
from typing import Optional, Dict, Any

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("⚠️  Ollama Python package not found. Install with: pip install ollama")


class OllamaGemmaTest:
    """Test class for Ollama with Gemma 3:1b model"""
    
    def __init__(self, model_name: str = "gemma2:1b"):
        self.model_name = model_name
        self.client = None
        
    def check_ollama_service(self) -> bool:
        """Check if Ollama service is running"""
        try:
            if not OLLAMA_AVAILABLE:
                return False
                
            # Try to connect to Ollama service
            response = ollama.list()
            print("✅ Ollama service is running")
            return True
        except Exception as e:
            print(f"❌ Ollama service is not running or accessible: {e}")
            print("   Make sure to start Ollama service with: ollama serve")
            return False
    
    def check_model_availability(self) -> bool:
        """Check if the Gemma model is available"""
        try:
            models = ollama.list()
            available_models = []
            
            # Debug: print the raw response
            print(f"🔍 Raw models response: {models}")
            
            if 'models' in models and models['models']:
                for model in models['models']:
                    # Try different possible keys for model name
                    name = model.get('name') or model.get('model') or model.get('id', 'Unknown')
                    available_models.append(name)
            
            print(f"📋 Available models: {available_models}")
            
            if self.model_name in available_models:
                print(f"✅ Model '{self.model_name}' is available")
                return True
            else:
                print(f"❌ Model '{self.model_name}' is not found")
                print(f"   Install with: ollama pull {self.model_name}")
                
                # Check if there's a similar model name
                similar_models = [m for m in available_models if 'gemma' in m.lower()]
                if similar_models:
                    print(f"   Similar models found: {similar_models}")
                    print(f"   You might want to use one of these instead.")
                
                return False
                
        except Exception as e:
            print(f"❌ Error checking models: {e}")
            print(f"   Details: {type(e).__name__}: {str(e)}")
            return False
    
    def test_simple_generation(self) -> bool:
        """Test simple text generation"""
        try:
            print(f"\n🧪 Testing simple generation with {self.model_name}...")
            
            prompt = "Hello! Can you tell me a short joke?"
            
            print(f"📝 Prompt: {prompt}")
            print("⏳ Generating response...")
            
            start_time = time.time()
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                stream=False
            )
            end_time = time.time()
            
            if response and 'response' in response:
                print(f"✅ Response generated successfully!")
                print(f"🤖 Response: {response['response']}")
                print(f"⏱️  Generation time: {end_time - start_time:.2f} seconds")
                
                # Print some stats if available
                if 'eval_count' in response:
                    print(f"📊 Tokens generated: {response.get('eval_count', 'N/A')}")
                if 'eval_duration' in response:
                    duration_ms = response['eval_duration'] / 1000000  # nanoseconds to milliseconds
                    print(f"📊 Evaluation duration: {duration_ms:.2f} ms")
                
                return True
            else:
                print("❌ No response generated")
                return False
                
        except Exception as e:
            print(f"❌ Error during generation: {e}")
            return False
    
    def test_streaming_generation(self) -> bool:
        """Test streaming text generation"""
        try:
            print(f"\n🧪 Testing streaming generation with {self.model_name}...")
            
            prompt = "Write a very short story about a robot learning to paint."
            
            print(f"📝 Prompt: {prompt}")
            print("⏳ Streaming response...")
            print("🤖 Response: ", end="", flush=True)
            
            start_time = time.time()
            full_response = ""
            
            for chunk in ollama.generate(
                model=self.model_name,
                prompt=prompt,
                stream=True
            ):
                if 'response' in chunk:
                    print(chunk['response'], end="", flush=True)
                    full_response += chunk['response']
            
            end_time = time.time()
            print()  # New line after streaming
            
            if full_response:
                print(f"✅ Streaming generation successful!")
                print(f"⏱️  Total time: {end_time - start_time:.2f} seconds")
                print(f"📊 Total characters: {len(full_response)}")
                return True
            else:
                print("❌ No streaming response received")
                return False
                
        except Exception as e:
            print(f"❌ Error during streaming: {e}")
            return False
    
    def test_conversation(self) -> bool:
        """Test conversation with context"""
        try:
            print(f"\n🧪 Testing conversation with {self.model_name}...")
            
            messages = [
                {"role": "user", "content": "My name is Alice. What's a good programming language to learn?"},
                {"role": "assistant", "content": "Python is an excellent choice for beginners! It has clear syntax and is very versatile."},
                {"role": "user", "content": "What's my name and why did you recommend Python?"}
            ]
            
            print("💬 Testing conversation context...")
            
            start_time = time.time()
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                stream=False
            )
            end_time = time.time()
            
            if response and 'message' in response:
                print(f"✅ Conversation test successful!")
                print(f"🤖 Response: {response['message']['content']}")
                print(f"⏱️  Response time: {end_time - start_time:.2f} seconds")
                return True
            else:
                print("❌ No conversation response received")
                return False
                
        except Exception as e:
            print(f"❌ Error during conversation: {e}")
            return False
    
    def get_model_info(self) -> bool:
        """Get detailed model information"""
        try:
            print(f"\n📋 Getting model information for {self.model_name}...")
            
            model_info = ollama.show(self.model_name)
            
            if model_info:
                print(f"✅ Model information retrieved!")
                print(f"📊 Model details:")
                
                # Print key information
                if 'details' in model_info:
                    details = model_info['details']
                    print(f"   - Format: {details.get('format', 'N/A')}")
                    print(f"   - Family: {details.get('family', 'N/A')}")
                    print(f"   - Parameter Size: {details.get('parameter_size', 'N/A')}")
                    print(f"   - Quantization Level: {details.get('quantization_level', 'N/A')}")
                
                if 'model_info' in model_info:
                    info = model_info['model_info']
                    if isinstance(info, dict):
                        for key, value in info.items():
                            if key not in ['tokenizer.chat_template']:  # Skip very long values
                                print(f"   - {key}: {value}")
                
                return True
            else:
                print("❌ Could not retrieve model information")
                return False
                
        except Exception as e:
            print(f"❌ Error getting model info: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        print("🚀 Starting Ollama Gemma 3:1b Test Suite")
        print("=" * 50)
        
        results = {}
        
        # Check if ollama package is available
        if not OLLAMA_AVAILABLE:
            print("❌ Ollama package not available. Please install with: pip install ollama")
            return {"package_available": False}
        
        results["package_available"] = True
        
        # Test 1: Check Ollama service
        results["service_running"] = self.check_ollama_service()
        if not results["service_running"]:
            return results
        
        # Test 2: Check model availability
        results["model_available"] = self.check_model_availability()
        if not results["model_available"]:
            return results
        
        # Test 3: Get model info
        results["model_info"] = self.get_model_info()
        
        # Test 4: Simple generation
        results["simple_generation"] = self.test_simple_generation()
        
        # Test 5: Streaming generation
        results["streaming_generation"] = self.test_streaming_generation()
        
        # Test 6: Conversation
        results["conversation"] = self.test_conversation()
        
        return results
    
    def print_summary(self, results: Dict[str, bool]):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! Ollama with Gemma 3:1b is working correctly!")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")


def main():
    """Main function to run the tests"""
    print("🤖 Ollama Gemma 3:1b Test Script")
    print("This script will test your Ollama installation with the Gemma 3:1b model.\n")
    
    # Allow custom model name
    model_name = "gemma2:1b"
    if len(sys.argv) > 1:
        model_name = sys.argv[1]
        print(f"Using custom model: {model_name}")
    
    # Create test instance
    tester = OllamaGemmaTest(model_name)
    
    # Run all tests
    results = tester.run_all_tests()
    
    # Print summary
    tester.print_summary(results)
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
