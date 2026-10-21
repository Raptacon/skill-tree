import yaml
import glob
import common

def validate_yaml():
    [yaml.safe_load(open(f)) for f in glob.glob('content/**/*.yml', recursive=True)]
    print('all yaml valid')

def is_skill_valid(tree_name, skill):
    return any(d.get("id") == skill for d in common.load_skills(tree_name).get("skills"))

if __name__ == "__main__":
    validate_yaml()