import os

from pydantic import BaseModel, NonNegativeInt

import common
import yaml

class OnePager(BaseModel):
    name: str
    grad_year: NonNegativeInt
    progress: dict[str, dict]
    interests: list[str]
    badges: list[str]

def validate_onepager(student_id): 
    student = common.load_yaml(f"students/{student_id}.yml")
    onepager = OnePager(**student)

def is_skill_valid(tree_name, skill):
    return any(d.get("id") == skill for d in common.load_skills(tree_name).get("skills"))

if __name__ == "__main__":
    print("wrong file")