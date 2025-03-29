import time
import json
from func.deepseek_helper import deepseek_helper

def section_splitter_ai(text_pages, header_tokens, output_json, url, model, api_key):

    user_prompt = f'''
    对从pdf文件中读取的所有页的文本进行处理。
    1，删除可能存在的页眉文字。页眉文字位于每页的头或尾，包含固定的文字或页码或日期等信息。
    2，删除多余的换行符。pdf文件由于页面的行宽限制，在文字到达页面边缘时，会自动进行换行。因此存在大量多余的换行符。
    3，内容以条目进行组。每个条目由条目头开头。条目头一般位于行首的位置，且有两种形式：
        形式1）由数字和点组成。e.g. 12.3. 或 1.22.4.3. 
        形式2）由固定单词 或 固定单词+数字组成。其中固定单词可以是{header_tokens}中的一个，不区分大小写。数字可以是罗马数字。e.g. Annex 1，Annex II，Chapter 1.
    '''
    start_time = time.time() 

    format_prompt = '''
    输入的json数组的格式为 [ 第1页的内容, 第2页的内容, ...]. 
    输出的json数组的格式为 [ [id, page_number, section_header, section_content], ...]。
    id为条目的序号，从0开始, e.g. id = 0
    page_number为页码，从page1开始, e.g. page_number = "Page 1"
    section_header为条目头，e.g. section_header = "2.4." or section_header = "Section"
    section_content为除了条目头以外的条目内容。
    '''

    try:
        sections = deepseek_helper(user_prompt + format_prompt, text_pages, url, model, api_key)
        if (isinstance(sections, list)):
            with open(output_json, "w", encoding='utf-8') as f:
                json.dump(sections, f, ensure_ascii=False, indent=4)
        else:
            print(f"deepseek output format error. ")

    except Exception as e:
        print(f" DeepSeek Output Error: {e}")
        
        
    end_time = time.time()
    print(f" Elapsed time during calling deepseek: {(end_time - start_time)/60:.1f} minutes")

    return sections



