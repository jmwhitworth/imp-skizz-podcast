
def get_day_suffix(day:int) -> str:
    """Returns the suffix for a given day of the month."""
    if 11 <= day <= 13:
        return 'th'
    return {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
