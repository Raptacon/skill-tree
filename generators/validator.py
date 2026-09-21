import os
from typing import Any

from pydantic import BaseModel, ConfigDict, NonNegativeInt, model_validator

import common
import yaml

class Progress(BaseModel):
    hours: NonNegativeInt
    passed: bool | None = None
    tier_verified: NonNegativeInt | None = None
    skills_completed: list[str] | None = None

class OnePager(BaseModel):
    name: str
    grad_year: NonNegativeInt
    progress: dict[str, Progress]
    interests: list[str]
    badges: list[str]
    
    @model_validator(mode='before')
    @classmethod
    def check_passed_value(cls, data: Any) -> Any:
        # custom handling for the progress value, since it doesnt appear in all trees
        if isinstance(data, dict):
            for tree_name, tree_value in data.get('progress').items():
                if tree_name == 'baseline' and 'passed' not in tree_value:
                    raise ValueError("baseline tree requires 'passed'")
                elif tree_name != 'baseline' and 'passed' in tree_value:
                    raise ValueError(f"value for 'passed' not allowed inside {tree_name} tree")      
        return data

def validate_onepager(student_id): 
    student = common.load_yaml(f"students/{student_id}.yml")
    onepager = OnePager(**student)

def is_skill_valid(tree_name, skill):
    return any(d.get("id") == skill for d in common.load_skills(tree_name).get("skills"))

if __name__ == "__main__":
    print("wrong file")