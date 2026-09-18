import os

import common
import yaml


def validate_onepager(student_id): 
    try:   
        student = common.load_yaml(f"students/{student_id}.yml")
    except yaml.YAMLError:
        msg = "error parsing yaml file"
    else:  
        msg = ""
        name = student.get("name")
        if name is None:
            msg += "expected a name, got none\n"
        grad_year = student.get("grad_year", None)
        if grad_year is None:
            msg += "expected grad year, got none\n"
        
        for tree_name, tree_value in student.get("progress").items():
            # verify hours
            hours = tree_value.get("hours")
            try:
                if hours < 0:
                    msg += "hours cannot be negative\n"
            except TypeError:
                msg += "hours must be an int\n"
                
            if tree_name == "baseline":
                # verify the one value in baseline tree
                passed = tree_value.get("passed")
                if not isinstance(passed, bool):
                    msg += "passed must be a bool\n"
            else:
                # we are likely outside baseline tree
                # verify tier_verified
                tier_verified = tree_value.get("tier_verified")
                try:
                    if tier_verified < 0 or tier_verified > 4:
                        msg += "tier_verified must be a number between 0 and 4\n"
                except TypeError:
                    msg += "tier_verified must be an int\n"
                    
                # verify that skills in student tree exist
                for skill_completed in tree_value.get("skills_completed"):
                    if not is_skill_valid(tree_name, skill_completed):
                        msg += f"invalid skill name '{skill_completed}'\n"
    return msg

def is_skill_valid(tree_name, skill):
    return any(d.get("id") == skill for d in common.load_skills(tree_name).get("skills"))

if __name__ == "__main__":
    print("wrong file")