import ollama

def summarize(text: str) -> str:
    prompt = f"""
你是一個專業的會議與文件摘要助手。
請將以下內容整理成「重點摘要」。

規則：
- 使用條列式
- 每點不超過 2 行
- 去除冗詞與重複敘述
- 使用繁體中文

內容：
{text}
"""

    response = ollama.chat(
        model="qwen3:8b",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response["message"]["content"]
