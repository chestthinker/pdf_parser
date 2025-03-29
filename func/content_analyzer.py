import time
import json
from func.deepseek_helper import deepseek_helper

def content_analyzer(sections, user_prompt, user_query, output_json, url, model, api_key):

    start_time = time.time()

    for query_index in range(len(user_query)):

        sections_inputs = [ [item[0]] + item[2:min(len(item),4)] for item in sections ]

        vis = [False] * len(sections)
        try_num = 0
        max_try_num = 10
        while (not all(vis)) and try_num < max_try_num:
            try_num += 1
            if try_num > 1:
                print(f" try: {try_num} for {len(unvis_indices)} sections ")

            unvis_indices = [index for index, value in enumerate(vis) if not value]

            format_prompt = f'''
            输入的json数组的格式为 [ [id, section_number, input_content, ...], [id, section_number, input_content, ...], ...]. 
            输入的json数组中每个值被定义为1个条目，共有{len(sections)}个条目。
            每个条目中包含多个值：id为条目的序号，section_number为章节号，其余为input_content。
            需处理id={unvis_indices}的条目。
            对这些条目中的 input_content 进行处理：{user_query[query_index]}，得到 output_content.
            输出的json数组的格式为 [ [id, section_number, output_content, ...], [id, section_number, output_content, ...], ...]
            输出条目第1个值为条目的id，第2个值为section_number，第3个值为处理后的结果。输出条目的id与输入条目的id相同。
            输出条目的总数为{len(unvis_indices)}，且与输入条目对应。
            不要合并任何条目进行输出，以免打乱输入和输出id的对应关系。
            '''

            print(f"\n Query DeepSeek {query_index+1}: \"{user_query[query_index]}\"")

            try:
                sections_outputs = deepseek_helper(user_prompt + format_prompt, sections_inputs, url, model, api_key)
                if (isinstance(sections_outputs, list)):
                    for sec in sections_outputs:
                        sections[int(sec[0])].append(sec[-1])
                        vis[int(sec[0])] = True
                else:
                    print(f"deepseek output format error. ")

            except Exception as e:
                print(f" DeepSeek Output Error: {e}")
        

    with open(output_json, "w", encoding='utf-8') as f:
        json.dump(sections, f, ensure_ascii=False, indent=4)
        
    end_time = time.time()
    print(f" Elapsed time during calling deepseek: {(end_time - start_time)/60:.1f} minutes")

    return sections



