# function to search the user's environment variables for VXD_HOME

import os

def get_vxd_home():
    VXD_HOME = None
    evars = os.environ
    VXD_HOME = evars.get('VXD_HOME')
    if VXD_HOME is None:
        print('Error: VXD_HOME environment variable has not been set')
        print('Please add the following lines to ~/.bash_profile (or equivalent)...')
        print('export VXD_HOME=<path to folder where VoxelDesk has been installed>')
        print('export PATH=${VXD_HOME}:${PATH}')
    return VXD_HOME