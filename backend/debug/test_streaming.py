import sys
import json
import urllib.request
import time

# Script to simulate a streaming chat client
URL = "http://localhost:8001/chat"

def chat_stream(query):
    print(f"🤖 Pergunta: '{query}'")
    print("⏳ Aguardando resposta...\n")
    print("--- INÍCIO DA RESPOSTA ---")
    
    data = json.dumps({"query": query}).encode("utf-8")
    req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"})
    
    try:
        with urllib.request.urlopen(req) as response:
            for line in response:
                decoded_line = line.decode("utf-8").strip()
                if decoded_line.startswith("data: "):
                    json_str = decoded_line[6:] # Remove 'data: ' prefix
                    try:
                        chunk = json.loads(json_str)
                        if chunk["type"] == "content":
                            # Print content without newline, flushing buffer immediately
                            sys.stdout.write(chunk["data"])
                            sys.stdout.flush()
                            # Simulate typing speed slightly if network is too fast (optional)
                            # time.sleep(0.01) 
                        elif chunk["type"] == "sources":
                            print("\n\n--- FIM DA RESPOSTA ---")
                            print(f"📚 Fontes: {chunk['data']}\n")
                    except json.JSONDecodeError:
                        pass
    except Exception as e:
        print(f"\n❌ Erro: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "O que é a santificação?"
    
    chat_stream(query)
