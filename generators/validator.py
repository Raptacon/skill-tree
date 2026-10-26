from datetime import date

from pydantic import BaseModel, Field, NonNegativeInt
import yaml
import glob
import common

class SkillTree(BaseModel):
    tree: Tree
    
class Tree(BaseModel):
    id: str
    name: str
    kind: str
    authored_by: list[dict[str, str]]
    created_at: date
    updated_at: date
    description: str

def validate_yaml():
    for file in glob.glob('content/raptacon/trees/*.yml', recursive=True):
        entries = yaml.safe_load(open(file))
        SkillTree(**entries)
        
    print('all yaml valid')

def is_skill_valid(tree_name, skill):
    return any(d.get("id") == skill for d in common.load_skills(tree_name).get("skills"))

if __name__ == "__main__":
    validate_yaml()