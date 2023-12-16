import json
from dataclasses import asdict, dataclass, fields, is_dataclass
from typing import Any, Dict, Type

def deserialize_dataclass(cls: Type, data: Dict[str, Any]):
    field_types = {f.name: f.type for f in fields(cls)}
    constructor_args = {}

    for field_name, field_type in field_types.items():
        if field_name in data:
            if is_dataclass(field_type):
                # Recursively deserialize nested dataclasses
                constructor_args[field_name] = deserialize_dataclass(field_type, data[field_name])
            else:
                constructor_args[field_name] = data[field_name]

    return cls(**constructor_args)

# Example usage
@dataclass
class ExampleNested:
    value: int

@dataclass
class Example:
    name: str
    nested: ExampleNested

def serialize_dataclass(obj):
    if is_dataclass(obj):
        return asdict(obj)
    raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)

#json_data = '{"name": "Test", "nested": {"value": 42}}'

content = Example(name="Test", nested=ExampleNested(value=42))
json_data = json.dumps(content, default=serialize_dataclass) #json.dumps(content)
dict_data = json.loads(json_data)

example_instance = deserialize_dataclass(Example, dict_data)
assert content == example_instance
print(example_instance)