# Lebab

Word docx translator, from one language to another (using OpenAI's GPT-4 model)

The script can be used as an example on how to access the OpenAI API with Python. For the most part created with OpenAI: ChatGPT and Copilot.

## Installation

Clone the repository. Use the dependency and package manager [Poetry](https://python-poetry.org/) to install all the dependencies of vein.

```bash
poetry install
```

## Usage

```bash
python lebab.py {source-file} {source language} {target language}
```
Lebab.py will create a copy of {source-file} with the name "{source-file}_{source language}.docx". 

## Configuration for usage with OpenAI

Create a text file _"dev.env"_ in the root of the project. This will contain the "OPENAI_API_KEY" environment variable used by the application to obtain the token associated to a valid OpenAI account when calling the API.

```bash
OPENAI_API_KEY=sk-A_seCR_et_key_GENERATED_foryou_by_OPENAI
```

The environment variable is loaded into the execution context of the application when run in the debugger if as such specified in the file _"launch.json"_. An example launch configuration shows how:

```json
{   //example launch configuration
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "lebab.py",
            "console": "integratedTerminal",
            "justMyCode": true,
            "envFile": "${workspaceFolder}/dev.env"
        }
    ]
}
```


## Usage
[Activate the Python virtual environment](https://python-poetry.org/docs/basic-usage/#activating-the-virtual-environment) with

```bash
poetry shell
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Copyright and license

Copyright © 2023 Iwan van der Kleijn

Licensed under the MIT License 
[MIT](https://choosealicense.com/licenses/mit/)