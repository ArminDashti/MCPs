import asyncio
import json
from src.run_python_code_tool import execute

async def main():
    sample_code = "import os;print(os.environ.get('CONDA_DEFAULT_ENV','unknown')); print('hiiiiiiiiii')"
    print("Running sample Python code in py312 environment")
    print("-" * 50)
    result = await execute({"code": sample_code})
    if result and len(result) > 0:
        response_text = result[0].text
        print("\nFull JSON Response:")
        print(response_text)
        data = json.loads(response_text)
        print("\nSummary:")
        print(f"  is_successful: {data.get('is_successful')}")
        result_text = data.get('result')
        if result_text:
            print("  result:")
            print(f"    {result_text}")
    else:
        print("No response received")

if __name__ == "__main__":
    asyncio.run(main())

