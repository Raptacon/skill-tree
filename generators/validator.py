from datetime import date

from pydantic import BaseModel
import yaml
import glob

class SkillTree(BaseModel):
    tree: Tree
    
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

def validate_yaml():
    for file in glob.glob('content/raptacon/trees/*.yml', recursive=True):
        entries = yaml.safe_load(open(file))
        SkillTree(**entries)
        
    print('all yaml valid')

if __name__ == "__main__":
    validate_yaml()