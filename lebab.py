import argparse
import asyncio
import os
import shutil
import tempfile

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI# Requires langchain>=0.3
import docx  # python-docx for Word files
from pptx import Presentation  # python-pptx for PowerPoint files
import json

load_dotenv()  # load environment variables from .env file
__DEBUG__ = os.getenv("DEBUG", "false").lower() == "true"


# Estimate a maximum character count per translation request.
MAX_CHUNK_SIZE = 10000

def init_llm():
    """
    Initialize the LLM using ChatOpenAI.
    """

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    # Create the ChatOpenAI instance.
    llm = ChatOpenAI(openai_api_key=openai_api_key, temperature=0, model_name="gpt-3.5-turbo")
    return llm

async def translate_blocks_json_async(blocks, input_lang, output_lang, llm):
    """
    Translate a JSON array of blocks asynchronously using the LLM.
    
    The function encodes the list of blocks as a JSON string and sends it along with a prompt
    that instructs the LLM to translate the "text" field for each block from input_lang to output_lang.
    The LLM is instructed to return a valid JSON array where each object has a new key 'translated_text'.
    """
    prompt = (
        f"Translate the following JSON array of objects from {input_lang} to {output_lang}. "
        "Each object has a 'text' field that must be translated. For each object, add a new key "
        "'translated_text' containing the translated text. Do not modify any other keys. "
        "Return only a valid JSON array with no additional commentary or formatting."
    )
    
    json_data = json.dumps(blocks, ensure_ascii=False)
    full_message = f"{prompt}\n\nJSON Input:\n{json_data}"
    
    try:
        response = await llm.ainvoke([{"role": "user", "content": full_message}])
        translated_json = response.content if hasattr(response, "content") else response
        # Parse and return the JSON output.
        translated_blocks = json.loads(translated_json)
        return translated_blocks
    except Exception as e:
        print(f"Error during translation: {e}")
        # On error, return the original blocks with a fallback.
        for block in blocks:
            block["translated_text"] = block.get("text", "")
        return blocks

class DocumentTranslator:
    """
    Base class for document translators.
    """
    def __init__(self, file_path):
        self.file_path = file_path
        self.blocks = []  # Each block represents a text unit from the document

    def read_document(self):
        raise NotImplementedError

    def write_document(self, target_path):
        raise NotImplementedError

    def update_blocks(self, translated_blocks):
        raise NotImplementedError

class DocxTranslator(DocumentTranslator):
    """
    Translator for Word (.docx) documents.
    """
    def __init__(self, file_path):
        super().__init__(file_path)
        self.doc = None

    def read_document(self):
        try:
            self.doc = docx.Document(self.file_path)
            self.blocks = []
            for i, para in enumerate(self.doc.paragraphs):
                self.blocks.append({"type": "paragraph", "index": i, "text": para.text})
        except Exception as e:
            print(f"Error reading DOCX file: {e}")

    def update_blocks(self, translated_blocks):
        for block in translated_blocks:
            if block["type"] == "paragraph":
                try:
                    self.doc.paragraphs[block["index"]].text = block["translated_text"]
                except Exception as e:
                    print(f"Error updating paragraph {block['index']}: {e}")

    def write_document(self, target_path):
        try:
            self.doc.save(target_path)
        except Exception as e:
            print(f"Error writing DOCX file: {e}")

class PptxTranslator(DocumentTranslator):
    """
    Translator for PowerPoint (.pptx) presentations.
    """
    def __init__(self, file_path):
        super().__init__(file_path)
        self.prs = None

    def read_document(self):
        try:
            self.prs = Presentation(self.file_path)
            self.blocks = []
            for slide_index, slide in enumerate(self.prs.slides):
                for shape_index, shape in enumerate(slide.shapes):
                    if hasattr(shape, "text") and shape.text:
                        self.blocks.append({
                            "type": "shape",
                            "slide_index": slide_index,
                            "shape_index": shape_index,
                            "text": shape.text
                        })
        except Exception as e:
            print(f"Error reading PPTX file: {e}")

    def update_blocks(self, translated_blocks):
        for block in translated_blocks:
            if block["type"] == "shape":
                try:
                    slide = self.prs.slides[block["slide_index"]]
                    shape = slide.shapes[block["shape_index"]]
                    shape.text = block["translated_text"]
                except Exception as e:
                    print(f"Error updating slide {block['slide_index']} shape {block['shape_index']}: {e}")

    def write_document(self, target_path):
        try:
            self.prs.save(target_path)
        except Exception as e:
            print(f"Error writing PPTX file: {e}")

async def process_translation(translator, input_lang, output_lang, llm):
    """
    Process the translation of document blocks in manageable chunks using a JSON-based approach.
    
    Blocks are accumulated until a maximum estimated character size is reached, then sent as a JSON array.
    The translated JSON array is parsed and merged back into the document model.
    """
    translator.read_document()
    if not translator.blocks:
        print("No text blocks found for translation.")
        return

    translated_blocks = []
    current_chunk = []
    current_chunk_size = 0

    for block in translator.blocks:
        block_text = block["text"]
        block_size = len(block_text)
        if current_chunk and (current_chunk_size + block_size > MAX_CHUNK_SIZE):
            translated_chunk = await translate_blocks_json_async(current_chunk, input_lang, output_lang, llm)
            for orig, trans in zip(current_chunk, translated_chunk):
                orig["translated_text"] = trans.get("translated_text", orig["text"])
            translated_blocks.extend(current_chunk)
            current_chunk = []
            current_chunk_size = 0

        current_chunk.append(block)
        current_chunk_size += block_size

    if current_chunk:
        translated_chunk = await translate_blocks_json_async(current_chunk, input_lang, output_lang, llm)
        for orig, trans in zip(current_chunk, translated_chunk):
            orig["translated_text"] = trans.get("translated_text", orig["text"])
        translated_blocks.extend(current_chunk)

    translator.update_blocks(translated_blocks)

def construct_target_filename(input_file, output_lang):
    base, ext = os.path.splitext(input_file)
    return f"{base}_{output_lang}{ext}"

async def main():
    parser = argparse.ArgumentParser(description="Lebab: Document Translator Preserving Structure")
    parser.add_argument("input_file", help="Path to the input document")
    parser.add_argument("input_lang", help="Input language code (e.g., ES)")
    parser.add_argument("output_lang", help="Output language code (e.g., EN)")
    parser.add_argument("-t", "--to-file", help="Target file path")
    args = parser.parse_args()

    input_file = args.input_file
    target_file = args.to_file if args.to_file else construct_target_filename(input_file, args.output_lang)

    try:
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, os.path.basename(input_file))
        shutil.copy(input_file, temp_file)
        print(f"Temporary file created at {temp_file}")
    except Exception as e:
        print(f"Error creating temporary file: {e}")
        return

    ext = os.path.splitext(input_file)[1].lower()
    if ext == ".docx":
        translator = DocxTranslator(temp_file)
    elif ext == ".pptx":
        translator = PptxTranslator(temp_file)
    else:
        print("Unsupported file format. Only .docx and .pptx are supported.")
        return

    try:
        llm = init_llm()
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        return

    await process_translation(translator, args.input_lang, args.output_lang, llm)
    translator.write_document(target_file)
    print(f"Translated document saved to {target_file}")

if __name__ == "__main__":
    asyncio.run(main())
