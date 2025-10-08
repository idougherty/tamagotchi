from ollama import chat
import re

MODEL = "hf.co/bartowski/Qwen_Qwen3-0.6B-GGUF:Q6_K"

def submit_prompt(system_prompt, user_prompt = None):
    messages = []
    messages.append({ "role": "system", "content": system_prompt })
    if user_prompt is not None:
        messages.append({ "role": "user", "content": user_prompt })
 
    print(system_prompt, user_prompt)

    response = chat(model=MODEL, messages=messages)

    answer = response['message']['content'].strip()
    print(f"LLM response {answer}")

    cleaned_content = re.sub(r"<think>.*?</think>\n?", "", answer, flags=re.DOTALL).strip()
    answer = cleaned_content if cleaned_content else answer

    emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               "]+", flags=re.UNICODE)
    answer = emoji_pattern.sub(r'', answer)

    answer = answer.strip('"')

    return answer
