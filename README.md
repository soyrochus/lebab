# Lebab: Document Translator Preserving Structure

Lebab is a Python console application and library that translates Word and PowerPoint documents using an LLM. Its core goal is to preserve the document’s structure and formatting during translation, making it an ideal solution for users who need accurate, structure-aware translations.


## Features

- **Modular Architecture:**  
  Easily extend Lebab to support additional document formats (e.g., Excel) by implementing new translator subclasses.
  
- **Document Structure Preservation:**  
  Translates individual text blocks (such as paragraphs in DOCX and text shapes in PPTX) without breaking the internal structure.
  
- **Chunked Translation:**  
  Groups text into manageable chunks (approximately 10K tokens estimated) to avoid overwhelming the LLM, ensuring each block remains intact.
  
- **Robust Error Handling:**  
  Catches errors during file reading, translation, and writing, allowing the process to continue even when individual blocks encounter issues.
  
- **Async LLM Invocation:**  
  Uses asynchronous LLM calls via `ainvoke` (with the `ChatOpenAI` class from LangChain) for efficient translation processing.
  
- **Environment-Based Configuration:**  
  Utilizes `python-dotenv` to securely manage your OpenAI API key and other sensitive settings.


## Requirements

- **Python 3.7+** (recommended)
- **Dependencies:**
  - [python-docx](https://python-docx.readthedocs.io/en/latest/)
  - [python-pptx](https://python-pptx.readthedocs.io/en/latest/)
  - [langchain](https://github.com/hwchase17/langchain) (version 0.3 or later)
  - [python-dotenv](https://pypi.org/project/python-dotenv/)


## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/lebab.git
   cd lebab
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   *If you don’t have a `requirements.txt` file yet, create one with the dependencies listed above.*

3. **Set up your environment:**

   Create a `.env` file in the project root and add your OpenAI API key:

   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

### Command Line

Lebab can be used directly from the command line. The basic syntax is:

```bash
python -m lebab <input_file> <input_lang> <output_lang> [--to-file <target_file>]
```

**Examples:**

- Translate a DOCX file from Spanish to English, writing output to a specific file:

  ```bash
  python -m lebab d:/tmp/mytext.docx ES EN --to-file=d:/tmp/mytext_EN.docx
  ```

- Translate a PPTX file from French to German. If the `--to-file` parameter is omitted, the output file will be generated by appending the target language to the original filename:

  ```bash
  python -m lebab d:/tmp/presentation.pptx FR DE
  ```

### As a Library

Lebab’s modular design allows you to integrate its functionality into your own Python applications. Import the necessary classes (e.g., `DocxTranslator`, `PptxTranslator`) and use them as part of your workflow.

## Project Structure & Development

- **`init_llm()` Function:**  
  Encapsulates the initialization of the LLM using `ChatOpenAI`, with API key retrieval via `python-dotenv`. This makes it simple to swap out the LLM initializer if needed.

- **Translator Classes:**  
  - **`DocumentTranslator`:** Base class defining the interface for document translation.
  - **`DocxTranslator`:** Handles Word documents using `python-docx`.
  - **`PptxTranslator`:** Handles PowerPoint documents using `python-pptx`.

- **Translation Process:**  
  The document is read, divided into text blocks, grouped into chunks to fit within a character limit, and each chunk is sent for translation. Translated text is then reassembled into the original document structure.

- **Error Handling:**  
  Robust error handling ensures that issues in reading, translation, or writing do not halt the overall process.


## Extending Lebab

To add support for another document format (e.g., Excel):

1. **Create a New Translator Class:**  
   Inherit from `DocumentTranslator` and implement the following methods:
   - `read_document()`
   - `update_blocks()`
   - `write_document()`

2. **Integrate Your Class:**  
   Update the main application logic to select your translator based on the file extension.


## Troubleshooting

- **API Key Issues:**  
  Ensure that your `.env` file is correctly configured with a valid `OPENAI_API_KEY`.

- **Unsupported Formats:**  
  Currently, only DOCX and PPTX are supported. For unsupported formats, extend the functionality by implementing a new translator.

- **Chunk Size Mismatch:**  
  In cases where the translated chunk does not split evenly back into blocks, a warning is printed and original text may be retained for those blocks.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Copyright and license

Copyright © 2025 Iwan van der Kleijn

Licensed under the MIT License 
[MIT](https://choosealicense.com/licenses/mit/)

*This project is provided as-is without any warranty. Enjoy translating your documents while preserving their original structure!*