#Lebab - Word docx translator, from one language to another - Copyright © 2023 Iwan van der Kleijn - See LICENSE.txt for conditions
import json
import sys
import os
from docx import Document
from openai import OpenAI
from dataclasses import dataclass, field
from typing import List
from dataclasses import is_dataclass, asdict


Paragraphs = List[str]

@dataclass
class Section:
    header: Paragraphs = field(default_factory=list)
    footer: Paragraphs = field(default_factory=list)

@dataclass
class Row:
    cells: List[Paragraphs] = field(default_factory=list) 
    
@dataclass
class Table:
    rows: List[Row] = field(default_factory=list)
    
@dataclass
class Content:
    paragraphs: Paragraphs = field(default_factory=list)
    tables: List[Table] = field(default_factory=list) 
    sections: List[Section] = field(default_factory=list)
    
    
def serialize_dataclass(obj):
    if is_dataclass(obj):
        return asdict(obj)
    raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)
    
def translate_data_structure(content, source_lang, target_lang):
    
    #turn dictionary into json
    json_content = json.dumps(content, default=serialize_dataclass) #json.dumps(content)
    
    return json_content
    
    # Constructing the prompt for translation
    translation_prompt = f"""Translate the following json structure from {source_lang} to {target_lang}: {json_content}

For lists: translate all text elements. For dictionaries: don't translate the keys of dictionary, only the values. 
Translate the values in the same order as they appear in the json structure.
Don't add any elements to the json structure, only translate the values of the existing elements.
Return the translated json structure. Do not return a string, but a json structure. Do not add any text as the
returned structure will be marshalled to Python.
""" 

    client = OpenAI()
    completion = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a profesional translator of many different languages. Your skill is the ability to strike a good ballance between semantic and communicative translation"},
        {"role": "user", "content": translation_prompt}
    ])
    
    translate_json = completion.choices[0].message.content
    translated_content = json.loads(translate_json)
    return translated_content

def _mock_translate_data_structure(content, source_lang, target_lang):
    return {'paragraphs': ['Este es un texto para ser traducido al español', 'Esta no es la imagen correcta']}

def get_content(doc):
    content = Content()
    for paragraph in doc.paragraphs:
        if text := paragraph.text.strip():
            content.paragraphs.append(text)
            
    # Extract text from tables
    for table in doc.tables:
        
        _table = Table(); content.tables.append(_table)
        for row in table.rows:
            _row = Row(); _table.rows.append(_row)
            for cell in row.cells:
                _cell = []; _row.cells.append(_cell)
                for paragraph in cell.paragraphs:
                    if text := paragraph.text.strip():
                        _cell.append(text)
        
    return content
    
def lebab(file_path, source_lang, target_lang):
    # Copy the file to a new file with the specified format
    new_file_path = f"{os.path.splitext(file_path)[0]}_{target_lang}.docx"
    doc = Document(file_path)
   
    doc.save(new_file_path)

    # Access the new file
    new_doc = Document(new_file_path)

    content = get_content(new_doc)

    print(content)
    translated_content = translate_data_structure(content, source_lang, target_lang)
    translated_content = _mock_translate_data_structure(content, source_lang, target_lang)
    print(translated_content)
    
    #take a list new_doc.paragraphs and overwrite each element with text (and NOT the list itself) with 
    #the "paragraphs" item from the translated_content dictionary
    i = 0
    for paragraph in new_doc.paragraphs:
        if text := paragraph.text.strip():
            paragraph.text = translated_content["paragraphs"][i]
            i += 1
    
    # Save the new file
    new_doc.save(new_file_path)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: lebab document.docx source_language target_language")
        sys.exit(1)

    file_path = sys.argv[1]
    source_lang = sys.argv[2]
    target_lang = sys.argv[3]

    print(f"Translating {file_path} from {source_lang} to {target_lang}")
    lebab(file_path, source_lang, target_lang)
