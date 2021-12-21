#!/usr/bin/env python

# program to write the config file, used in the vxd tools

import json
from vxdTools.get_vxd_home import get_vxd_home
import os

def writeConfigFile():
    config = {}
    config['sortedDicomFolderName'] = 'vxd_dicom'
    config['sortedNiftiFolderName'] = 'vxd_nifti'
    config['defaultTargetPattern'] = '/%PatientName/%StudyDate/%SeriesNumber-%SeriesDescription/%SeriesDescription-%InstanceNumber.dcm'
    config['excludeNifti'] = ['localizer', 'survey', 'phoenix', 'iso_tensor']
    config['deidRecipe'] = 'deid_voxelDesk.dicom'


    # Serializing json
    json_object = json.dumps(config, indent=4)

    # Writing to config.json
    VXD_HOME = get_vxd_home()
    if VXD_HOME is None:
        print("writeConfigFile Error: Unable to write config.json as VXD_HOME environment variable has not been set")
        exit(1)
    else:
        outFilePath = os.path.join(VXD_HOME, 'vxdSetup', 'config.json')
        with open(outFilePath, "w") as outfile:
            outfile.write(json_object)





