#Lebab - Word docx translator, from one language to another - Copyright © 2023 Iwan van der Kleijn - See LICENSE.txt for conditions
import json
import sys
import os
from docx import Document #type: ignore
from openai import OpenAI
from dataclasses import dataclass, field, fields
from typing import Any, Dict, List, Type
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
    
def deserialize_from_json(json_str: str) -> Content:
    json_dict = json.loads(json_str)
    
    # Deserialize tables
    tables = []
    for table_dict in json_dict.get("tables", []):
        rows = [Row(cells=row_dict.get("cells", [])) for row_dict in table_dict.get("rows", [])]
        tables.append(Table(rows=rows))
    
    # Deserialize sections (if necessary, depending on your JSON structure)
    sections = [Section(header=sec_dict.get("header", []), footer=sec_dict.get("footer", [])) for sec_dict in json_dict.get("sections", [])]

    return Content(paragraphs=json_dict.get("paragraphs", []), tables=tables, sections=sections)


def serialize_dataclass(obj:Any)-> Dict[str, Any]:
    if is_dataclass(obj):
        return asdict(obj)
    raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)

def translate_json(json_content: str, source_lang: str, target_lang:str)-> str:
        
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
    
    translated_json = completion.choices[0].text #type: ignore
    if translate_json is None:
        raise Exception("No translation returned")
    return translated_json 

def translate_data_structure(content: Content, source_lang: str, target_lang:str)-> Content:
    
    #turn dictionary into json
    json_content = json.dumps(content, default=serialize_dataclass) 
    print(json_content)

    translate_json = '{"paragraphs": ["Este es un texto para ser traducido al español", "Esta no es la imagen correcta"], "tables": [{"rows": [{"cells": [["Esta es la primera celda"], ["Los vikingos no eran llamados así"]]}, {"cells": [["¿Qué es lo que quieres?"], ["Congelado en el tiempo"]]}]}], "sections": []}'
    #translate_json = translate_json(json_content, source_lang, target_lang)

    print(translate_json)
    translated_content = deserialize_from_json(translate_json)  # type: ignore
    return translated_content

def get_content(doc: Document):
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
                _cell = []; _row.cells.append(_cell) # type: ignore
                for paragraph in cell.paragraphs:
                    if text := paragraph.text.strip():
                        _cell.append(text)
        
    return content

def set_content(doc: Document, content):
    #take a list new_doc.paragraphs and overwrite each element with text (and NOT the list itself) with 
    #the "paragraphs" item from the translated_content dictionary
   
    p_i=0
    for paragraph in doc.paragraphs:
        if text := paragraph.text.strip():
            paragraph.text = content.paragraphs[p_i]
            p_i += 1
            
    # overwrite the text in the tables
    t_i= 0
    for table in doc.tables:
        r_i = 0
        for row in table.rows:
            c_i = 0
            for cell in row.cells:
                p_i=0
                for paragraph in cell.paragraphs:
                    if text := paragraph.text.strip():
                        paragraph.text = content.tables[t_i].rows[r_i].cells[c_i][p_i]
                        p_i += 1
                c_i += 1
            r_i += 1
        t_i += 1
        
            
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
    print(translated_content)
  
    set_content(new_doc, translated_content)
    
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
