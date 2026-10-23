from pydantic import BaseModel, Field, NonNegativeInt
import yaml
import glob
import common

class SkillTree(BaseModel):
    tree: str
    skills: list[Skills]
    
class Skills(BaseModel):
    id: str
    tier: NonNegativeInt = Field(le=4)
    name: str
    description: str

def validate_yaml():
    for file in glob.glob('content/raptacon/skills/*.yml', recursive=True):
        entries = yaml.safe_load(open(file))
        SkillTree(**entries)
        
    print('all yaml valid')

def is_skill_valid(tree_name, skill):
    return any(d.get("id") == skill for d in common.load_skills(tree_name).get("skills"))

if __name__ == "__main__":
    validate_yaml()