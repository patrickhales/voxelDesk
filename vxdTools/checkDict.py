def checkDict(dict, requirements):
    """function to check the list of parameters defined in requirements are not set to None in the passed dict"""
    missing_values = []
    for param in requirements:
        if dict[param] is None:
            missing_values.append(param)
    if not missing_values:
        return 0
    else:
        raise Exception('Missing required values: %s' % missing_values)