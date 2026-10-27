from datetime import date
from typing import Any, Self

from pydantic import BaseModel, ModelWrapValidatorHandler, ValidationError, model_validator
import yaml
import glob

class SkillTree(BaseModel):
    tree: Tree
    items: Item    
    
class Tree(BaseModel):
    id: str
    name: str
    kind: str
    parent_trees: list[str] | None = None
    requires: list[str] | None = None
    authored_by: list[dict[str, str]]
    created_at: date
    updated_at: date
    description: str
    
class Item(BaseModel):
    id: str
    name: str
    description: str
    section: str
    roles: str
    kind: str
    requires: list[str]
    verify: dict[str, str]
    renews: str
    visibility: str

def validate_yaml():
    for file in glob.glob('content/raptacon/trees/*.yml', recursive=True):
        entries = yaml.safe_load(open(file))
        print(f"validating '{file}'...")
        SkillTree(**entries)
        
    print('all yaml valid')

if __name__ == "__main__":
    validate_yaml()