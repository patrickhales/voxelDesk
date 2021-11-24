import os
import json
from vxdTools.get_vxd_home import get_vxd_home
def readConfigFile():

    "function to read in the config file, based on the VXD_HOME environment variable"

    # read system environment variables, and look for the VXD_HOME variable
    VXD_HOME = get_vxd_home()
    if VXD_HOME is None:
        config = None
    else:
        # open the config file to load in default values used in processing
        with open(os.path.join(VXD_HOME, 'vxdSetup', 'config.json'), 'r') as infile:
            config = json.load(infile)

        # add the VXD_HOME location to the config dict
        config['VXD_HOME'] = VXD_HOME

    return config
