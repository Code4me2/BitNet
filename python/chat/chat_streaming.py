#!/usr/bin/env python3
"""
BitNet Chat Interface with Streaming Output
Real-time token generation display
"""
import subprocess
import os
import sys
import re
import time
import json
import threading
import queue
from datetime import datetime
from pathlib import Path

class BitNetStreamingChat:
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
        print("║" + " BitNet B1.58 2B4T Streaming Chat ".center(width-2) + "║")
        print("║" + " " * (width-2) + "║")
        print("║" + f" Model: {os.path.basename(self.model_path)[:40]}".ljust(width-2) + "║")
        print("║" + f" Temperature: {self.settings['temperature']} | Max Tokens: {self.settings['max_tokens']}".ljust(width-2) + "║")
        print("║" + " " * (width-2) + "║")
        print("║" + " Commands: /help /settings /clear /save /exit ".center(width-2) + "║")
        print("═" * width + "\n")
        
    def extract_response_streaming(self, process):
        """Extract response from streaming output"""
        response_started = False
        response_lines = []
        current_line = ""
        assistant_found = False
        tokens_count = 0
        start_time = time.time()
        
        while True:
            # Read character by character for real-time output
            char = process.stdout.read(1)
            
            if not char:
                # Process finished
                break
                
            # Build current line
            current_line += char
            
            # Check if we've found the assistant marker
            if not assistant_found and "Assistant:" in current_line:
                assistant_found = True
                # Extract everything after "Assistant:"
                parts = current_line.split("Assistant:")
                if len(parts) > 1:
                    current_line = parts[-1]
                    response_started = True
            
            # If we're in the response section
            if response_started:
                # Check for technical output markers that indicate end of response
                tech_markers = ["build:", "main:", "llama_", "llm_", "warning:", "ggml_"]
                
                # Check if line contains technical marker
                marker_found = False
                for marker in tech_markers:
                    if marker in current_line:
                        # Split at marker and keep only the part before
                        parts = current_line.split(marker)
                        if parts[0].strip():
                            # Print remaining part before marker
                            remaining = parts[0].rstrip()
                            if remaining and not remaining.isspace():
                                print(remaining, end='', flush=True)
                                response_lines.append(remaining)
                        marker_found = True
                        break
                
                if marker_found:
                    # Stop reading response
                    break
                
                # Print character immediately if it's printable
                if char.isprintable() or char in '\n\t':
                    print(char, end='', flush=True)
                    
                    # Count tokens (rough estimate)
                    if char in ' \n\t':
                        tokens_count += 1
                
                # Handle newlines
                if char == '\n':
                    response_lines.append(current_line.rstrip())
                    current_line = ""
        
        # Add any remaining line
        if current_line.strip() and response_started:
            response_lines.append(current_line.rstrip())
        
        # Read remaining output to clear buffer and get performance metrics
        remaining_output = process.stdout.read()
        process.wait()
        
        # Calculate generation time
        generation_time = time.time() - start_time
        
        # Extract performance metrics from stderr or remaining output
        all_output = remaining_output + (process.stderr.read() if process.stderr else "")
        perf_match = re.search(r'(\d+\.?\d*)\s*tokens per second', all_output)
        tokens_per_sec = float(perf_match.group(1)) if perf_match else 0
        
        # Join response lines
        full_response = '\n'.join(response_lines).strip()
        
        # Clean up response
        full_response = ''.join(char for char in full_response if char.isprintable() or char in '\n\t')
        
        return {
            "response": full_response,
            "generation_time": generation_time,
            "tokens_per_second": tokens_per_sec,
            "token_count": tokens_count,
            "success": bool(full_response)
        }
        
    def generate_response_streaming(self, prompt):
        """Generate response with streaming output"""
        # Build conversation context
        context_messages = []
        for role, msg, _ in self.conversation_history[-6:]:  # Last 3 exchanges
            context_messages.append(f"{role.capitalize()}: {msg}")
        
        full_prompt = f"{self.system_prompt}\n\n"
        if context_messages:
            full_prompt += '\n\n'.join(context_messages) + "\n\n"
        full_prompt += f"User: {prompt}\n\nAssistant:"
        
        # Build command for llama-cli directly for better streaming
        if os.name == 'nt':  # Windows
            llama_cli = "build/bin/Release/llama-cli.exe"
            if not os.path.exists(llama_cli):
                llama_cli = "build/bin/llama-cli.exe"
        else:
            llama_cli = "build/bin/llama-cli"
            
        cmd = [
            llama_cli,
            "-m", self.model_path,
            "-p", full_prompt,
            "-n", str(self.settings['max_tokens']),
            "--temp", str(self.settings['temperature']),
            "-t", str(self.settings['threads']),
            "--top-k", str(self.settings.get('top_k', 40)),
            "--top-p", str(self.settings.get('top_p', 0.95)),
            "--repeat-penalty", str(self.settings.get('repeat_penalty', 1.1)),
            "-ngl", "0",
            "-c", "2048",
            "-b", "1"
        ]
        
        try:
            # Start process with pipes
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1  # Line buffered
            )
            
            # Extract response with streaming
            result = self.extract_response_streaming(process)
            
            return result
            
        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "success": False,
                "generation_time": 0,
                "tokens_per_second": 0,
                "token_count": 0
            }
    
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
        
    def save_conversation(self):
        """Save conversation to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_logs/bitnet_streaming_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write(f"BitNet Streaming Chat Session\n")
            f.write(f"Date: {datetime.now()}\n")
            f.write(f"System Prompt: {self.system_prompt}\n")
            f.write("=" * 60 + "\n\n")
            
            for role, msg, ts in self.conversation_history:
                f.write(f"[{ts}] {role.capitalize()}:\n{msg}\n\n")
                
        print(f"\n💾 Conversation saved to {filename}")
        input("\nPress Enter to continue...")
    
    def show_help(self):
        """Show help message"""
        help_text = """
Commands:
  /help         - Show this help message
  /settings     - View and modify chat settings
  /clear        - Clear conversation history
  /save         - Save conversation to file
  /system       - Quick change system prompt
  /temp <value> - Quick change temperature (0.0-1.0)
  /tokens <n>   - Quick change max tokens
  /exit         - Exit the chat

Tips:
  - Lower temperature (0.1-0.5) for more focused responses
  - Higher temperature (0.7-1.0) for more creative responses
  - Text appears as it's generated for a natural feel
        """
        print(help_text)
        input("\nPress Enter to continue...")
        
    def run(self):
        """Main chat loop"""
        self.print_banner()
        
        print("💡 Tip: Text will appear as it's being generated!\n")
        
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
                        self.save_conversation()
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
                
                # Generate response with streaming
                print("\n🤖 BitNet: ", end='', flush=True)
                
                result = self.generate_response_streaming(user_input)
                
                if result['success']:
                    # Response already printed via streaming
                    print()  # New line after response
                    
                    # Show performance metrics
                    if result.get('tokens_per_second', 0) > 0:
                        print(f"\n📊 [{result['token_count']} tokens, "
                              f"{result['generation_time']:.1f}s, "
                              f"{result['tokens_per_second']:.1f} tok/s]")
                    
                    # Add to history
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    self.conversation_history.append(("user", user_input, timestamp))
                    self.conversation_history.append(("assistant", result['response'], timestamp))
                    
                    # Keep history manageable
                    if len(self.conversation_history) > 20:
                        self.conversation_history = self.conversation_history[-20:]
                else:
                    print(f"\n❌ {result['response']}")
                    
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
        
    # Check llama-cli binary
    if os.name == 'nt':  # Windows
        llama_cli = "build/bin/Release/llama-cli.exe"
        if not os.path.exists(llama_cli):
            llama_cli = "build/bin/llama-cli.exe"
    else:
        llama_cli = "build/bin/llama-cli"
        
    if not os.path.exists(llama_cli):
        print("❌ Error: llama-cli binary not found!")
        print(f"Expected location: {llama_cli}")
        print("Please run the build process first.")
        sys.exit(1)
    
    # Run chat
    chat = BitNetStreamingChat(model_path)
    chat.run()

if __name__ == "__main__":
    main()