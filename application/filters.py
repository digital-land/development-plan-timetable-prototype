def get_date_part(d_str, part):
    parts = d_str.split("-")
    if part == "YYYY":
        return parts[0]
    if part == "MM":
        return parts[1]
    return parts[2]
