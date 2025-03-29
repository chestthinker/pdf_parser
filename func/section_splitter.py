import os
import re
import json

def section_splitter(text_pages, header_tokens, page_header, output_json):
    """Process multiline text into structured sections with headers and contents"""

    text_pages = [ txt_process(page, header_tokens, page_header) for page in text_pages ]
    #
    text_lines = [ [f"Page {page_num + 1}", line] for page_num, pages in enumerate(text_pages) for line in pages.split('\n') ]

    sections = []
    current_header = None
    current_content = []

    # Compile regex patterns for header detection
    numeric_header = re.compile(r'^(\d+\.)+')  # Matches numeric patterns like 1.2.
    token_header = None
    
    if header_tokens:
        # Build pattern for token headers with Roman/digit suffixes
        token_pattern = (
            r'^(' + '|'.join(map(re.escape, header_tokens)) + ')'  # Match heading tokens
            r'\s*([IVXLCDM]+|\d+)[\.\s]*'  # Followed by Roman/digit with optional dot/space
        )
        token_header = re.compile(token_pattern, flags=re.IGNORECASE)

    get_first_header = False
    current_content_first = []
    page_num = 1
    section_id = 0
    for row in text_lines:

        line = row[1]
        # Skip empty lines and comments
        stripped = line.strip()
        if not stripped or line.startswith('#--'):
            continue

        header = None
        content_rest = ''

        # Check token headers if no numeric match
        exception_str = ['Article 7(6) in conjunction', '3.5.3.2.']

        if  not( (line[:len(exception_str[0])] == exception_str[0]) and (row[0] == "Page 1")  ) and \
            not( (line[:len(exception_str[1])] == exception_str[1]) and (row[0] == "Page 12") ):
        
            # Check numeric headers first
            if numeric_header.match(line):
                header_match = numeric_header.match(line)
                header = header_match.group().strip()
                content_rest = line[header_match.end():].lstrip()

            if (not header and token_header):
                token_match = token_header.match(line)
                if token_match:
                    header = token_match.group().strip()
                    content_rest = line[token_match.end():].lstrip()

        if header:
            if not get_first_header:
                sections.append([section_id, 'Page 1', "", '\n'.join(current_content_first)])
                section_id += 1
                get_first_header = True

            # Finalize current section
            if current_header is not None:
                sections.append([section_id, page_num, current_header, '\n'.join(current_content)])
                section_id += 1
                current_content = []       

            # Start new section
            current_header = header
            page_num = row[0]
            if content_rest:
                current_content.append(content_rest)
            
        else:
            # Accumulate content lines
            if (current_header is not None):
                current_content.append(line)

            if  (not get_first_header):
                current_content_first.append(line)

    # Add final section
    if current_header is not None:
        sections.append([section_id, page_num, current_header, '\n'.join(current_content)])        
        section_id += 1
    with open(output_json, "w", encoding='utf-8') as f:
        json.dump(sections, f, ensure_ascii=False, indent=4)

    print(f" Complete: -> {os.path.basename(output_json)}  Sections: {len(sections)}")

    return sections


def txt_process(str, header_tokens, page_header):
    # processing
    str = convert_chinese_punctuation(str)
    str = re.sub('(' + page_header + ').*', '', str) # Delete page header
    str = remove_unexpect_line_break(str, header_tokens)                
    str = re.sub(r'(\. ){8,}', '   ', str) # Replace continous dot more than 8 with '  '

    return str

def remove_unexpect_line_break(text, header_tokens):

    lines = text.split('\n')
    result = []
    previous_line = ''
    
    for current_line in lines:
        
        current_line = current_line.strip()
        # Condition 1: Current line starts with English word (no leading space)
        starts_with_word = re.match(r'^[A-Za-z]', current_line)
        # Condition 2: Previous line ends with word or comma (may have trailing space)
        prev_ends_with_word = re.search(r'[A-Za-z,\.\-()]\s*$', previous_line.strip())
        
        if starts_with_word and prev_ends_with_word:
            # Extract first word for heading check
            first_word = re.split(r'\s+', current_line.lstrip())[0].lower()           

            # Check against heading tokens (case-insensitive)
            if first_word not in [token.lower() for token in header_tokens]:
                # Merge with cleaned whitespace
                if previous_line[-1] == '-':
                    previous_line += '' + current_line.lstrip()
                else:
                    previous_line += ' ' + current_line.lstrip()
                continue
        
        # Preserve current state
        result.append(previous_line)
        previous_line = current_line
    
    # Add final line
    if previous_line:
        result.append(previous_line)
    
    return '\n'.join(result)

def convert_chinese_punctuation(text):

    # Mapping of Chinese punctuation to English equivalents
    punctuation_map = {
        '，': ',',  # Chinese comma
        '。': '.',  # Chinese period
        '；': ';',  # Chinese semicolon
        '：': ':',  # Chinese colon
        '！': '!',  # Chinese exclamation
        '？': '?',  # Chinese question mark
        '“': '"',   # Left Chinese double quote
        '”': '"',   # Right Chinese double quote
        '‘': "'",   # Left Chinese single quote
        '’': "'",   # Right Chinese single quote
        '（': '(',  # Chinese left parenthesis
        '）': ')',  # Chinese right parenthesis
        '【': '[',  # Chinese left square bracket
        '】': ']',  # Chinese right square bracket
        '《': '<',  # Chinese left angle bracket
        '》': '>',  # Chinese right angle bracket
        '～': '~',  # Chinese tilde
        '—': '-',   # Chinese dash
        '–': '-',   # Chinese dash
        '…': '...',# Chinese ellipsis
        '、': ','   # Chinese enumeration comma
    }
    
    # Create translation table using the mapping
    translation_table = str.maketrans(punctuation_map)
    
    # Apply translation table for common replacements
    return text.translate(translation_table)

