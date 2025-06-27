#!/usr/bin/env python3
"""
Advanced BitNet Chat Interface with streaming-like output and better formatting
"""
import subprocess
import os
import sys
import re
import time
import json
from datetime import datetime
from pathlib import Path

class BitNetChatAdvanced:
    def __init__(self, model_path="models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf"):
        self.model_path = model_path
        self.conversation_history = []
        self.system_prompt = "You are a helpful AI assistant."
        self.settings = {
            "temperature": 0.7,
            "max_tokens": 200,
            "threads": 10,  # Using 10 threads for optimal performance
            "top_k": 40,
            "top_p": 0.95,
            "repeat_penalty": 1.1
        }
        
        # Set environment variables
        os.environ['OMP_NUM_THREADS'] = str(self.settings['threads'])
        os.environ['MKL_NUM_THREADS'] = str(self.settings['threads'])
        
        # Create logs directory
        Path("chat_logs").mkdir(exist_ok=True)
        
    def print_banner(self):
        """Print a nice banner"""
        width = 70
        print("\n" + "═" * width)
        print("║" + " BitNet B1.58 2B4T Advanced Chat Interface ".center(width-2) + "║")
        print("║" + " " * (width-2) + "║")
        print("║" + f" Model: {os.path.basename(self.model_path)[:40]}".ljust(width-2) + "║")
        print("║" + f" Temperature: {self.settings['temperature']} | Max Tokens: {self.settings['max_tokens']}".ljust(width-2) + "║")
        print("║" + " " * (width-2) + "║")
        print("║" + " Commands: /help /settings /clear /save /export /exit ".center(width-2) + "║")
        print("═" * width + "\n")
        
    def simulate_typing(self, text, delay=0.01):
        """Simulate typing effect for more natural feel"""
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print()
        
    def format_response(self, text):
        """Format the response text for better readability"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Add proper line breaks
        words = text.split()
        lines = []
        current_line = []
        line_length = 0
        
        for word in words:
            if line_length + len(word) + 1 > 80:  # 80 char width
                lines.append(' '.join(current_line))
                current_line = [word]
                line_length = len(word)
            else:
                current_line.append(word)
                line_length += len(word) + 1
        
        if current_line:
            lines.append(' '.join(current_line))
            
        return '\n'.join(lines)
        
    def show_settings(self):
        """Display current settings"""
        print("\n" + "─" * 50)
        print("Current Settings:")
        print("─" * 50)
        for key, value in self.settings.items():
            print(f"  {key:15s}: {value}")
        print(f"  {'system_prompt':15s}: {self.system_prompt[:50]}...")
        print("─" * 50)
        
    def change_settings(self):
        """Interactive settings changer"""
        self.show_settings()
        print("\nWhich setting would you like to change?")
        print("(Enter setting name or 'cancel' to go back)")
        
        setting = input("> ").strip().lower()
        
        if setting == 'cancel' or not setting:
            return
            
        if setting == 'system_prompt':
            print(f"\nCurrent: {self.system_prompt}")
            new_value = input("New system prompt: ").strip()
            if new_value:
                self.system_prompt = new_value
                print("✅ System prompt updated!")
        elif setting in self.settings:
            print(f"\nCurrent {setting}: {self.settings[setting]}")
            try:
                if setting in ['temperature', 'top_p', 'repeat_penalty']:
                    new_value = float(input(f"New {setting}: "))
                else:
                    new_value = int(input(f"New {setting}: "))
                self.settings[setting] = new_value
                
                # Update environment variables if needed
                if setting == 'threads':
                    os.environ['OMP_NUM_THREADS'] = str(new_value)
                    os.environ['MKL_NUM_THREADS'] = str(new_value)
                    
                print(f"✅ {setting} updated to {new_value}!")
            except ValueError:
                print("❌ Invalid value!")
        else:
            print(f"❌ Unknown setting: {setting}")
            
        input("\nPress Enter to continue...")
        
    def export_conversation(self, format='json'):
        """Export conversation in different formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == 'json':
            filename = f"chat_logs/bitnet_chat_{timestamp}.json"
            data = {
                "timestamp": datetime.now().isoformat(),
                "system_prompt": self.system_prompt,
                "settings": self.settings,
                "conversation": [
                    {"role": role, "content": msg, "timestamp": ts}
                    for role, msg, ts in self.conversation_history
                ]
            }
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
        else:  # markdown
            filename = f"chat_logs/bitnet_chat_{timestamp}.md"
            with open(filename, 'w') as f:
                f.write(f"# BitNet Chat Session\n\n")
                f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**System Prompt**: {self.system_prompt}\n\n")
                f.write("---\n\n")
                
                for role, msg, ts in self.conversation_history:
                    f.write(f"### {role.capitalize()} ({ts})\n\n")
                    f.write(f"{msg}\n\n")
                    
        print(f"\n💾 Conversation exported to {filename}")
        input("\nPress Enter to continue...")
        
    def generate_response(self, prompt):
        """Generate response with better error handling"""
        # Build conversation context
        context_messages = []
        for role, msg, _ in self.conversation_history[-6:]:  # Last 3 exchanges
            context_messages.append(f"{role.capitalize()}: {msg}")
        
        full_prompt = f"{self.system_prompt}\n\n"
        if context_messages:
            full_prompt += '\n\n'.join(context_messages) + "\n\n"
        full_prompt += f"User: {prompt}\n\nAssistant:"
        
        # Build command
        cmd = [
            "python3", "run_inference.py",
            "-m", self.model_path,
            "-p", full_prompt,
            "-n", str(self.settings['max_tokens']),
            "-temp", str(self.settings['temperature']),
            "-t", str(self.settings['threads']),
            "-top_k", str(self.settings.get('top_k', 40)),
            "-top_p", str(self.settings.get('top_p', 0.95)),
            "-repeat_penalty", str(self.settings.get('repeat_penalty', 1.1))
        ]
        
        try:
            # Show thinking animation
            print("Thinking", end='', flush=True)
            thinking_thread = True
            
            # Run the command
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
            generation_time = time.time() - start_time
            
            # Clear thinking animation
            print("\r" + " " * 20 + "\r", end='', flush=True)
            
            if result.returncode == 0:
                output = result.stdout
                
                # Extract response
                assistant_marker = "Assistant:"
                if assistant_marker in output:
                    response_start = output.rfind(assistant_marker) + len(assistant_marker)
                    response = output[response_start:].strip()
                    
                    # Clean technical output
                    for marker in ["build:", "main:", "llama_", "llm_", "warning:", "ggml_"]:
                        if marker in response:
                            response = response.split(marker)[0].strip()
                    
                    # Remove any non-printable characters
                    response = ''.join(char for char in response if char.isprintable() or char in '\n\t')
                    
                    # Extract performance metrics
                    perf_match = re.search(r'(\d+\.?\d*)\s*tokens per second', result.stderr + result.stdout)
                    tokens_per_sec = float(perf_match.group(1)) if perf_match else 0
                    
                    # Count tokens (rough estimate)
                    token_count = len(response.split()) * 1.3
                    
                    return {
                        "response": response.strip(),
                        "generation_time": generation_time,
                        "tokens_per_second": tokens_per_sec,
                        "token_count": int(token_count),
                        "success": True
                    }
                else:
                    return {
                        "response": "I couldn't generate a proper response. Please try again.",
                        "success": False
                    }
            else:
                return {
                    "response": f"Error generating response: {result.stderr[:200]}",
                    "success": False
                }
                
        except subprocess.TimeoutExpired:
            print("\r" + " " * 20 + "\r", end='', flush=True)
            return {
                "response": "Response generation timed out. Try reducing max_tokens or simplifying your prompt.",
                "success": False
            }
        except Exception as e:
            print("\r" + " " * 20 + "\r", end='', flush=True)
            return {
                "response": f"Unexpected error: {str(e)}",
                "success": False
            }
    
    def show_help(self):
        """Show detailed help"""
        help_text = """
Commands:
  /help         - Show this help message
  /settings     - View and modify chat settings
  /clear        - Clear conversation history
  /save         - Save conversation as text file
  /export       - Export conversation (json or markdown)
  /system       - Quick change system prompt
  /temp <value> - Quick change temperature (0.0-1.0)
  /tokens <n>   - Quick change max tokens
  /exit         - Exit the chat

Tips:
  - Lower temperature (0.1-0.5) for more focused responses
  - Higher temperature (0.7-1.0) for more creative responses
  - Adjust max_tokens for longer/shorter responses
  - Use /clear to reset context if responses become confused
        """
        print(help_text)
        input("\nPress Enter to continue...")
        
    def run(self):
        """Main chat loop"""
        self.print_banner()
        
        while True:
            try:
                # Show prompt
                user_input = input("\n💭 You: ").strip()
                
                if not user_input:
                    continue
                    
                # Handle commands
                if user_input.startswith('/'):
                    parts = user_input.split(maxsplit=1)
                    command = parts[0].lower()
                    args = parts[1] if len(parts) > 1 else ""
                    
                    if command == '/exit':
                        print("\n👋 Goodbye! Thanks for chatting!")
                        break
                    elif command == '/help':
                        self.show_help()
                        self.print_banner()
                    elif command == '/settings':
                        self.change_settings()
                        self.print_banner()
                    elif command == '/clear':
                        self.conversation_history = []
                        self.print_banner()
                        print("🗑️  Conversation cleared!")
                    elif command == '/save':
                        self.export_conversation('text')
                        self.print_banner()
                    elif command == '/export':
                        format_type = args.lower() if args in ['json', 'markdown'] else 'json'
                        self.export_conversation(format_type)
                        self.print_banner()
                    elif command == '/system':
                        if args:
                            self.system_prompt = args
                            print(f"✅ System prompt updated!")
                        else:
                            print(f"Current: {self.system_prompt}")
                    elif command == '/temp':
                        try:
                            self.settings['temperature'] = float(args)
                            print(f"✅ Temperature set to {self.settings['temperature']}")
                        except:
                            print("❌ Invalid temperature value")
                    elif command == '/tokens':
                        try:
                            self.settings['max_tokens'] = int(args)
                            print(f"✅ Max tokens set to {self.settings['max_tokens']}")
                        except:
                            print("❌ Invalid token count")
                    else:
                        print(f"❌ Unknown command: {command}")
                    continue
                
                # Generate response
                print("\n🤖 BitNet: ", end='', flush=True)
                
                result = self.generate_response(user_input)
                
                if result['success']:
                    # Format and display response
                    formatted_response = self.format_response(result['response'])
                    print(formatted_response)
                    
                    # Show performance metrics
                    if result.get('tokens_per_second', 0) > 0:
                        print(f"\n📊 [{result['token_count']} tokens, "
                              f"{result['generation_time']:.1f}s, "
                              f"{result['tokens_per_second']:.1f} tok/s]")
                    
                    # Add to history
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    self.conversation_history.append(("user", user_input, timestamp))
                    self.conversation_history.append(("assistant", result['response'], timestamp))
                else:
                    print(f"❌ {result['response']}")
                    
            except (EOFError, KeyboardInterrupt):
                print("\n\n👋 Goodbye! Thanks for chatting!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                
def main():
    """Main entry point"""
    # Check model
    model_path = "models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf"
    
    if not os.path.exists(model_path):
        print("❌ Error: Model file not found!")
        print(f"Expected location: {model_path}")
        sys.exit(1)
    
    # Run chat
    chat = BitNetChatAdvanced(model_path)
    chat.run()

if __name__ == "__main__":
    main()