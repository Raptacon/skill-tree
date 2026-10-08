import os
from typing import Any, Union

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt, ValidationError, model_validator
from pydantic_core import InitErrorDetails, PydanticCustomError

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
        errors = []
        for tree_name, tree_value in self.progress.items():
            if tree_name == "baseline":
                continue
            for skill in tree_value.skills_completed:
                if not is_skill_valid(tree_name, skill):
                    errors.append(
                        InitErrorDetails(
                            type=PydanticCustomError('invalid_skill', f"skill '{skill}' is invalid for tree '{tree_name}'"),
                            input=skill,
                        )
            )

        if errors:
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=errors,
            )
        return self 

def validate_onepager(student_id): 
    student = common.load_yaml(f"students/{student_id}.yml")
    onepager = OnePager(**student)

def is_skill_valid(tree_name, skill):
    return any(d.get("id") == skill for d in common.load_skills(tree_name).get("skills"))

if __name__ == "__main__":
    print("wrong file")