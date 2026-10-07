import os
from typing import Any, Union

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt, model_validator

import common
import yaml

class BaselineTree(BaseModel):
    model_config = ConfigDict(extra='forbid')
    hours: NonNegativeInt
    passed: bool
    
class ProgressTree(BaseModel):
    model_config = ConfigDict(extra='forbid')
    hours: NonNegativeInt
    tier_verified: NonNegativeInt = Field(le=4)
    skills_completed: list[str]

class OnePager(BaseModel):
    name: str
    grad_year: NonNegativeInt
    progress: dict[str, Union[BaselineTree, ProgressTree]]
    interests: list[str]
    badges: list[str]
    
    @model_validator(mode="after")
    def verify_completed_skills_exist(self):
        for tree_name, tree_value in self.progress.items():
            if tree_name == "baseline":
                continue
            for skill in tree_value.skills_completed:
                if not is_skill_valid(tree_name, skill):
                    raise ValueError(f"'{skill}' is an invalid completed skill for tree '{tree_name}'")
        return self 

def validate_onepager(student_id): 
    student = common.load_yaml(f"students/{student_id}.yml")
    onepager = OnePager(**student)

def is_skill_valid(tree_name, skill):
    return any(d.get("id") == skill for d in common.load_skills(tree_name).get("skills"))

if __name__ == "__main__":
    print("wrong file")