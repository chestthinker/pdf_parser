

def deepseek_helper(prompt, inputs, url, model, api_key):

    prompt_sep = \
    '''
    输入的内容在json数组中，由<JSON_BEGIN>和<JSON_END>标识开始和结束。
    输出的内容也在json数组中。同样以<JSON_BEGIN>和<JSON_END>作为开始和结束的标识符。 
    '''

    # compact json form
    input_json = json.dumps(inputs, ensure_ascii=False, indent=0, separators=(',', ':')) 

    input_prompt = prompt_sep + prompt + '\n<JSON_BEGIN>\n' + input_json + '\n<JSON_End>\n'

    completion_text = call_deepseek(input_prompt, url, model, api_key)
    outputs = fetch_json_token(completion_text)
    return outputs



import json
import re
def fetch_json_token(text):
    
    # non-greedy mode（.*?）
    pattern = r'<JSON_BEGIN>(.*?)<JSON_END>'
    match = re.search(pattern, text, re.DOTALL) 

    if match:
        result = match.group(1).strip()
        arr = json.loads(result)
        return arr
 

import openai
def call_deepseek(content, url, model, api_key):

    '''
    model:
        "Pro/deepseek-ai/DeepSeek-R1",              # paid,  671B, 64K
        "deepseek-ai/DeepSeek-R1",                  # bonus, 671B, 64K
        "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",  # free,    7B, 32K
        "Qwen/Qwen2.5-7B-Instruct",                 # free,    7B, 32K
    '''

    client = openai.OpenAI(api_key=api_key, base_url=url)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'user', 
            'content': content}
        ],
        temperature=0,  
        max_tokens=16384,
        stream=True
    )

    contents = ''
    reasonings = ''
    reasoning_begin = False
    content_begin = False
    for chunk in response:
        reasoning = chunk.choices[0].delta.reasoning_content
        content = chunk.choices[0].delta.content  

        if reasoning:
            if not reasoning_begin:
                print('<< Reasoning >>')
                reasoning_begin = True
            print(reasoning, end='')
            reasonings += reasoning

        if content:
            if not content_begin:
                print('<< Content >>')
                content_begin = True
            print(content, end='')
            contents += content
        
    return contents


