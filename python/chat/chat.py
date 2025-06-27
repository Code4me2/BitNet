#!/usr/bin/env python3
"""
BitNet B1.58 2B4T Interactive Chat Interface
"""
import subprocess
import os
import sys
import re
from datetime import datetime

class BitNetChat:
    def __init__(self, model_path="models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf"):
        self.model_path = model_path
        self.conversation_history = []
        self.system_prompt = "You are a helpful AI assistant."
        
        # Set environment variables for optimal performance
        # Using 10 threads for optimal performance on this system
        os.environ['OMP_NUM_THREADS'] = '10'
        os.environ['MKL_NUM_THREADS'] = '10'
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def print_header(self):
        """Print the chat interface header"""
        self.clear_screen()
        print("=" * 60)
        print("🤖 BitNet B1.58 2B4T Chat Interface")
        print("=" * 60)
        print(f"Model: {os.path.basename(self.model_path)}")
        print(f"Threads: {os.environ.get('OMP_NUM_THREADS', 'default')}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        print("Commands:")
        print("  /help     - Show this help message")
        print("  /clear    - Clear conversation history")
        print("  /system   - Change system prompt")
        print("  /save     - Save conversation to file")
        print("  /exit     - Exit the chat")
        print("=" * 60)
        print()
        
    def generate_response(self, prompt, max_tokens=200, temperature=0.7):
        """Generate a response using the BitNet model"""
        # Build the full prompt with conversation history
        full_prompt = self.system_prompt
        
        # Add conversation history
        for role, message in self.conversation_history[-5:]:  # Keep last 5 exchanges
            if role == "user":
                full_prompt += f"\n\nUser: {message}"
            else:
                full_prompt += f"\n\nAssistant: {message}"
        
        # Add current user input
        full_prompt += f"\n\nUser: {prompt}\n\nAssistant:"
        
        # Run inference
        cmd = [
            "python3", "../benchmarks/run_inference.py",
            "-m", self.model_path,
            "-p", full_prompt,
            "-n", str(max_tokens),
            "-temp", str(temperature),
            "-t", "10"  # Using 10 threads for optimal performance
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60)
            
            if result.returncode == 0:
                # Extract the generated text from output
                output = result.stdout
                
                # Find where the prompt ends and response begins
                response_start = output.find("Assistant:") + len("Assistant:")
                if response_start > len("Assistant:") - 1:
                    response = output[response_start:].strip()
                    
                    # Remove any technical output that might be included
                    # Split by common technical output markers
                    for marker in ["build:", "main:", "llama_", "llm_", "warning:"]:
                        if marker in response:
                            response = response.split(marker)[0].strip()
                    
                    # Clean up the response
                    response = response.strip()
                    
                    # Remove any non-printable characters
                    response = ''.join(char for char in response if char.isprintable() or char in '\n\t')
                    
                    # Extract performance info if available
                    perf_match = re.search(r'(\d+\.?\d*)\s*tokens per second', result.stderr + result.stdout)
                    perf_info = f" [{perf_match.group(1)} tok/s]" if perf_match else ""
                    
                    return response, perf_info
                else:
                    return "I couldn't generate a response. Please try again.", ""
            else:
                return f"Error: {result.stderr[:200]}", ""
                
        except subprocess.TimeoutExpired:
            return "Response generation timed out. Please try a shorter prompt.", ""
        except Exception as e:
            return f"Error: {str(e)}", ""
    
    def save_conversation(self):
        """Save the conversation to a file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bitnet_chat_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write(f"BitNet Chat Session - {datetime.now()}\n")
            f.write(f"System Prompt: {self.system_prompt}\n")
            f.write("=" * 60 + "\n\n")
            
            for role, message in self.conversation_history:
                f.write(f"{role.capitalize()}: {message}\n\n")
        
        print(f"\n💾 Conversation saved to {filename}")
        input("\nPress Enter to continue...")
        
    def change_system_prompt(self):
        """Change the system prompt"""
        print("\nCurrent system prompt:")
        print(f"  {self.system_prompt}")
        print("\nEnter new system prompt (or press Enter to keep current):")
        new_prompt = input("> ").strip()
        
        if new_prompt:
            self.system_prompt = new_prompt
            print("✅ System prompt updated!")
        else:
            print("System prompt unchanged.")
        
        input("\nPress Enter to continue...")
        
    def run(self):
        """Main chat loop"""
        self.print_header()
        print(f"System: {self.system_prompt}\n")
        
        while True:
            # Get user input
            try:
                user_input = input("\n🧑 You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\n👋 Goodbye!")
                break
                
            if not user_input:
                continue
                
            # Handle commands
            if user_input.startswith('/'):
                command = user_input.lower()
                
                if command == '/exit':
                    print("\n👋 Goodbye!")
                    break
                elif command == '/clear':
                    self.conversation_history = []
                    self.print_header()
                    print(f"System: {self.system_prompt}\n")
                    print("🗑️  Conversation history cleared!")
                elif command == '/help':
                    self.print_header()
                    print(f"System: {self.system_prompt}\n")
                elif command == '/save':
                    self.save_conversation()
                    self.print_header()
                    print(f"System: {self.system_prompt}\n")
                    # Reprint conversation history
                    for role, message in self.conversation_history[-3:]:
                        if role == "user":
                            print(f"\n🧑 You: {message}")
                        else:
                            print(f"\n🤖 BitNet: {message}")
                elif command == '/system':
                    self.change_system_prompt()
                    self.print_header()
                    print(f"System: {self.system_prompt}\n")
                else:
                    print(f"❌ Unknown command: {command}")
                continue
            
            # Generate response
            print("\n🤖 BitNet: ", end='', flush=True)
            print("Thinking...", end='\r', flush=True)
            
            response, perf_info = self.generate_response(user_input)
            
            # Clear the "Thinking..." message and print response
            print(" " * 20, end='\r')  # Clear the line
            print(f"🤖 BitNet: {response}")
            
            if perf_info:
                print(f"\n📊 Performance: {perf_info}")
            
            # Add to conversation history
            self.conversation_history.append(("user", user_input))
            self.conversation_history.append(("assistant", response))
            
            # Keep conversation history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

def main():
    """Main entry point"""
    # Check if model exists
    model_path = "models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf"
    
    if not os.path.exists(model_path):
        print("❌ Error: Model file not found!")
        print(f"Expected location: {model_path}")
        print("\nPlease run the setup process first.")
        sys.exit(1)
    
    # Start chat interface
    chat = BitNetChat(model_path)
    
    try:
        chat.run()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()