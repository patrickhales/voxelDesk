import json

def appendJson(jsonFile, newdata, prefix=None):
    """ function to append a dictionary to an existing json file"""

    if not isinstance(newdata, dict):
        raise Exception('<newdata> should be a dict, but was passed a %s' % type(newdata))

    # open the json file
    with open(jsonFile, "r") as infile:
        jsondat = json.load(infile)

    for param in newdata:
        if prefix is not None and isinstance(prefix, str):
            jsondat[prefix + '_' + param] = newdata[param]
        else:
            jsondat[param] = newdata[param]

    # Serializing json
    json_object = json.dumps(jsondat, indent=4)

    # Writing out
    with open(jsonFile, "w") as outfile:
        outfile.write(json_object)