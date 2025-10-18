from ollama import chat
import re

# MODEL = "hf.co/bartowski/Qwen_Qwen3-0.6B-GGUF:Q6_K"
MODEL = "qwen-litest"

def strip_emojis(text):
    EMOJI_PATTERN = re.compile(
        "["
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251" 
        "]+"
    )
    return EMOJI_PATTERN.sub(r'', text)


def submit_prompt(system_prompt, user_prompt = None, options = {}):
    messages = []
    messages.append({ "role": "system", "content": system_prompt })
    if user_prompt is not None:
        messages.append({ "role": "user", "content": user_prompt + " /no_think" })
 
    print(system_prompt, user_prompt)

    response = chat(model=MODEL, messages=messages, options=options)

    answer = response['message']['content'].strip()
    print(f"LLM response {answer}")

    # remove reasoning
    cleaned_content = re.sub(r"<think>.*?</think>\n?", "", answer, flags=re.DOTALL).strip()
    answer = cleaned_content if cleaned_content else answer

    answer = strip_emojis(answer)   # remove emojis
    answer = answer.strip('"')      # remove quotes
    answer = answer.strip()         # remove leading/trailing whitespace

    return answer
