import argparse
import requests
import json
import uuid
import sys

def send_query(query: str, webhook_url: str):
    payload = {
        "message": {
            "type": "tool-calls",
            "toolCalls": [
                {
                    "id": str(uuid.uuid4()),
                    "type": "function",
                    "function": {
                        "name": "query_codebase",
                        "arguments": json.dumps({"query": query})
                    }
                }
            ]
        }
    }

    print("\nSending query to DevWhisper...")
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        
        # DevWhisper's webhook returns JSON with a 'results' list
        data = response.json()
        results = data.get("results", [])
        
        if not results:
            print("No results returned from DevWhisper.")
            return

        for res in results:
            print(f"\nResponse:\n{res.get('result')}\n")
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with DevWhisper: {e}")
        if response is not None and hasattr(response, "text"):
             print(f"Server replied: {response.text}")

def main():
    parser = argparse.ArgumentParser(description="Standalone Test Client for DevWhisper")
    parser.add_argument("--query", "-q", type=str, help="Text query to send to DevWhisper", required=False)
    parser.add_argument("--url", "-u", type=str, default="http://localhost:8000/webhook", help="DevWhisper webhook URL")
    
    args = parser.parse_args()

    if args.query:
        send_query(args.query, args.url)
        return

    print("=== DevWhisper Standalone Test Client ===")
    print("Type your query below. Type 'exit' or 'quit' to stop.")
    
    while True:
        try:
            query = input("\nEnter query: ").strip()
            if not query:
                continue
            if query.lower() in ['exit', 'quit']:
                break
            send_query(query, args.url)
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)
        except EOFError:
            break

if __name__ == "__main__":
    main()
