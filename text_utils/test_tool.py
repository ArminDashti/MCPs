import asyncio
import json
from src.summarize_text_tool import execute

async def main():
    test_text = "Artificial intelligence is transforming the way we work and live. Machine learning algorithms can now process vast amounts of data to identify patterns and make predictions. Natural language processing enables computers to understand and generate human language. These technologies are being applied across various industries including healthcare, finance, and education. The future holds even more exciting possibilities as AI continues to evolve and improve."
    
    print("Testing summarize_text tool")
    print("-" * 50)
    
    result = await execute({
        "text": test_text,
        "sentence_count": 3,
        "method": "lsa",
        "language": "english"
    })
    
    if result and len(result) > 0:
        response_text = result[0].text
        print("\nFull JSON Response:")
        print(response_text)
        
        try:
            data = json.loads(response_text)
            if "error" in data:
                print(f"\nError: {data['error']}")
            else:
                print(f"\nSummary:")
                print(f"  Method: {data.get('method', 'N/A')}")
                print(f"  Language: {data.get('language', 'N/A')}")
                print(f"  Sentence Count: {data.get('sentence_count', 0)}")
                print(f"  Original Length: {data.get('original_length', 0)} characters")
                print(f"  Summary Length: {data.get('summary_length', 0)} characters")
                print(f"\nSummary Text:")
                print(f"  {data.get('summary', 'N/A')}")
        except json.JSONDecodeError:
            print("Failed to parse JSON response")
    else:
        print("No response received")

if __name__ == "__main__":
    asyncio.run(main())

