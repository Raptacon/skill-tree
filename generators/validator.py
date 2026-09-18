def validate_context(context):
    msg = ""
    name = context.get("name", None) 
    if name is None:
        msg += "expected a name, got none\n"
    grad_year = context.get("grad_year", None)
    if grad_year is None:
        msg += "expected grad year, got none\n"
    for _, tree_row in enumerate(context.get("tree_rows", None)):
        hours = tree_row.get("hours")
        try:
            if hours < 0:
                msg += "hours cannot be negative\n"
        except TypeError:
            msg += "hours must be an int\n"
            
        if tree_row.get("name", None) == "Baseline":
            passed = tree_row.get("passed")
            if not isinstance(passed, bool):
                msg += "passed must be a bool\n"
        else:
            tier_verified = tree_row.get("tiered")
            try:
                if tier_verified < 0 or tier_verified > 4:
                    msg += "tier_verified must be a number between 0 and 4\n"
            except TypeError:
                msg += "tier_verified must be an int\n"
    return msg