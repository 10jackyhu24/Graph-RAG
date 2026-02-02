import ollama
import os
import json

async def summarize(text: str) -> dict:
    # print(f"User: {text}")

    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # system_prompt_path = os.path.join(current_dir, "system_prompt.txt")
    # with open(system_prompt_path, "r", encoding="utf-8") as file:
    #     system_prompt = file.read()

    # extraction_schema_path = os.path.join(current_dir, "extraction_schema.json")
    # with open(extraction_schema_path, "r", encoding="utf-8") as file:
    #     extraction_schema = json.load(file)

    # response = ollama.chat(
    #     model="qwen3:8b",
    #     messages=[
    #         {"role": "system", "content": system_prompt},
    #         {"role": "user", "content": text}
    #     ],
    #     format=extraction_schema, # The core constraint
    #     options={
    #         'temperature': 0,      # High determinism for extraction
    #         'num_ctx': 32768       # Qwen3 supports large context
    #     },
    #     stream=True
    # )

    # response_content = ""
    # print("Response: ", end='', flush=True)
    # for chunk in response:
    #     content = chunk['message']['content']
    #     print(content, end='', flush=True)
    #     response_content += content

    # print()

    # response_dict = json.loads(response_content)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(current_dir, "../../test/test.json")
    with open(test_file_path, 'r', encoding='utf-8') as f:
        response_dict = json.load(f)
    # print(response_dict)
    return response_dict
