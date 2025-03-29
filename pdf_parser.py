"""
PDF Parser

This script provides end-to-end processing of PDF documents including:
- PDF text extraction
- Section segmentation
- Content analysis using AI models
- Excel report generation

Author: wanglei 00567749
Created: 2025-03-16
Version: 1.0.0
Email: wanglei888@huawei.com
"""


import argparse
import os
import json
from func.write_to_excel import write_to_excel
from func.content_analyzer import content_analyzer
from func.read_from_pdf import read_from_pdf
from func.section_splitter import section_splitter
from func.section_splitter_ai import section_splitter_ai
from func.utils import find_first_pdf


# ---------------------------
# Main Execution Pipeline
# ---------------------------
if __name__ == "__main__":
    '''
    Execution Example:
    python pdf_parser.py "EU 2021-646.pdf"
    '''

    # Create logging directory if not exists
    os.makedirs('log', exist_ok=True)

    # Configure command line arguments
    parser = argparse.ArgumentParser(description='parse the pdf file')
    parser.add_argument('-f', '--fname', type=str, 
                      default=find_first_pdf(),  # Auto-detect PDF if not specified
                      help='Input PDF file path')
    args = parser.parse_args()

    # Load configuration settings
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    base_url = config['llm']['base_url']
    model_id = config['llm']['model_id']
    api_key = config['llm']['api_key']

    # Determine processing mode from config
    mode = config["general"]["mode"]  # "Normal" (full processing) or "Refine" (incremental update)

    # ---------------------------
    # Processing Stage 1: PDF Text Extraction
    # ---------------------------
    pdf_path = args.fname
    output_json = config['pdf_scan']['output_filename']
    print(f"\n[Step 1] PDF Scanning ") 
    
    # Bypass extraction if in refine mode and cached data exists
    if mode == "Refine" and os.path.exists(output_json):
        with open(output_json, 'r', encoding='utf-8') as f:
            text = json.load(f)
        print(f" Import: <- \"{os.path.basename(output_json)}\" - Pages: {len(text)}")
    else:
        text = read_from_pdf(pdf_path, output_json)

    # ---------------------------
    # Processing Stage 2: Document Section Segmentation
    # ---------------------------
    output_json = config['section_split']['output_filename']
    header_tokens = config['section_split']['header_tokens']
    page_header = config['section_split']['page_header']
    print("\n[Step 2] Section Splitting ")    
    
    # Bypass segmentation if in refine mode and cached data exists
    if mode == "Refine" and os.path.exists(output_json):  
        with open(output_json, 'r', encoding='utf-8') as f:
            sections = json.load(f)
        print(f" Import: <- \"{os.path.basename(output_json)}\" - Sections: {len(sections)}")
    else:
        #sections = section_splitter_ai(text, header_tokens, output_json, base_url, model_id, api_key)
        sections = section_splitter(text, header_tokens, page_header, output_json)

    # ---------------------------
    # Processing Stage 3: AI Content Analysis
    # ---------------------------
    output_json = config['content_analyze']['output_filename']
    user_prompt = config['content_analyze']['user_prompt']
    user_query = config['content_analyze']['user_query']
    print(f"\n[Step 3] Content Analyzing ")

    # Bypass analyzing if in refine mode and cached data exists
    if mode == "Refine" and os.path.exists(output_json):        
        with open(output_json, 'r', encoding='utf-8') as f:
            sections = json.load(f)
        print(f" Import: <- \"{os.path.basename(output_json)}\" - Sections: {len(sections)}")
    else:
        sections = content_analyzer(sections, user_prompt, user_query, 
                                  output_json, base_url, model_id, api_key)
    
    # ---------------------------
    # Processing Stage 4: Excel Report Generation
    # ---------------------------
    output_xls = config['excel_generate']['output_filename']
    row_height = config['excel_generate']['row_height']
    col_width = config['excel_generate']['col_width']
    title = config['excel_generate']['title']
    print(f"\n[Step 4] EXCEL File Generating ")
    write_to_excel(sections, output_xls, row_height, col_width, title)



