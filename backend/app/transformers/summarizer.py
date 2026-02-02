import ollama
import os

async def summarize(text: str) -> str:
    print(f"User: {text}")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    system_prompt_path = os.path.join(current_dir, "system_prompt.txt")
    with open(system_prompt_path, "r", encoding="utf-8") as file:
        system_prompt = file.read()

    response = ollama.chat(
        model="qwen3:8b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        stream=True
    )

    response_content = ""
    print("Response: ", end='', flush=True)
    for chunk in response:
        content = chunk['message']['content']
        print(content, end='', flush=True)
        response_content += content

    print()


    return response_content
