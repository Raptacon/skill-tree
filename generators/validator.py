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
        
        for tree in student.get("progress").values():
            # verify hours
            hours = tree.get("hours")
            try:
                if hours < 0:
                    msg += "hours cannot be negative\n"
            except TypeError:
                msg += "hours must be an int\n"
                
            if tree.get("name", None) == "Baseline":
                # verify the one value in baseline tree
                passed = tree.get("passed")
                if not isinstance(passed, bool):
                    msg += "passed must be a bool\n"
            else:
                # we are likely outside baseline tree
                # verify tier_verified
                tier_verified = tree.get("tiered")
                try:
                    if tier_verified < 0 or tier_verified > 4:
                        msg += "tier_verified must be a number between 0 and 4\n"
                except TypeError:
                    msg += "tier_verified must be an int\n"
    return msg

if __name__ == "__main__":
    print("wrong file")