def kebab_case(s):
    # Convert the s to lowercase and replace any spaces or underscores with hyphens
    s = s.lower().replace(" ", "-").replace("_", "-")
    # Remove any consecutive hyphens
    while "--" in s:
        s = s.replace("--", "-")
    # Remove any leading or trailing hyphens
    s = s.strip("-")
    return s
