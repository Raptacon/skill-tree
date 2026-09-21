import os
from typing import Any, Union

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt, model_validator

import common
import yaml

class Baseline(BaseModel):
    model_config = ConfigDict(extra='forbid')
    hours: NonNegativeInt
    passed: bool
    
class Progress(BaseModel):
    model_config = ConfigDict(extra='forbid')
    hours: NonNegativeInt
    tier_verified: NonNegativeInt
    skills_completed: list[str]

class OnePager(BaseModel):
    name: str
    grad_year: NonNegativeInt
    progress: dict[str, Union[Baseline, Progress]]
    interests: list[str]
    badges: list[str]

def validate_onepager(student_id): 
    student = common.load_yaml(f"students/{student_id}.yml")
    onepager = OnePager(**student)

def is_skill_valid(tree_name, skill):
    return any(d.get("id") == skill for d in common.load_skills(tree_name).get("skills"))

if __name__ == "__main__":
    print("wrong file")