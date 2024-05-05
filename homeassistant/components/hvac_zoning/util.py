"""File for utilities."""


def filter_to_valid_zones(user_input):
    """Filter to valid zones."""
    return sorted(
        {
            area
            for areas in user_input.values()
            for area in areas
            if area in user_input["temperature"] and area in user_input["damper"]
        }
    )
