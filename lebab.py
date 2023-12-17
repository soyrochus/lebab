#Lebab - Word docx translator, from one language to another - Copyright © 2023 Iwan van der Kleijn - See LICENSE.txt for conditions
import sys, os
from docx import Document #type: ignore
from openai import OpenAI

SEPERATOR = "\n⸻⸻⸻⸻⸻\n"

def translate_content(content: str, source_lang: str, target_lang:str)-> str:
        
    # Constructing the prompt for translation
    translation_prompt = f"""Translate the following text from {source_lang} to {target_lang}: 

The text  consists of text elements seperated by the following seperator: {SEPERATOR}

Leave the seperator in place, and translate the text elements in between the seperators.
Don't change the seperator itself. Dont'a add anything to the text elements, or remove anything from them.

The text follows below:

{content}
""" 

    client = OpenAI()
    completion = client.chat.completions.create(
    #model="gpt-4",
    model="gpt-4-1106-preview",
    messages=[
        {"role": "system", "content": "You are a profesional translator of many different languages. Your skill is the ability to strike a good ballance between semantic and communicative translation"},
        {"role": "user", "content": translation_prompt}
    ])
    
    translated_content = completion.choices[0].message.content
    if translated_content is None:
        raise Exception("No translation returned")
    return translated_content 


def get_content(doc: Document) -> str:
    content_items = []
    for paragraph in doc.paragraphs:
        if text := paragraph.text.strip():
            content_items.append(text)
            
    # Extract text from tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    if text := paragraph.text.strip():
                        content_items.append(text)
    
    # Join the content items with the seperator
    return SEPERATOR.join(content_items)

def set_content(doc: Document, content:str):
    # Split the content into content items
   
    content_items = content.split(SEPERATOR)
    # overwrite the text in the paragraphs
    p_i=0
    for paragraph in doc.paragraphs:
        if text := paragraph.text.strip():
            paragraph.text = content_items[p_i]
            p_i += 1
            
    # overwrite the text in the tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    if text := paragraph.text.strip():
                        paragraph.text = content_items[p_i]
                        p_i += 1
     
            
def lebab(file_path, source_lang, target_lang):
    # Copy the file to a new file with the specified format
    new_file_path = f"{os.path.splitext(file_path)[0]}_{target_lang}.docx"
    doc = Document(file_path)
   
    doc.save(new_file_path)

    # Access the new file
    new_doc = Document(new_file_path)

    content = get_content(new_doc)

    print(content)
    translated_content = translate_content(content, source_lang, target_lang)
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
    print("Done")
