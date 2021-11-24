# function to collate the DICOM header info from standard tags and Siemens CSA tags into one class

import pydicom
from vxdDicom.read_siemens_csa import read_siemens_csa
import os
import sys
from vxdTools.get_vxd_home import get_vxd_home

def collate_dicom_info(dcmFile=None):
    ds_csa = None
    if dcmFile is not None:

        # read the standard and CSA header info
        ds = pydicom.read_file(dcmFile, stop_before_pixels=True)
        csa = read_siemens_csa(dcmFile=dcmFile)

        # make a combined ds + csa dict (remember ds is not a straight-forward dict)
        # TODO: If Dicoms are from the Vida, in enhanced mode, I don't think the CSA header is present
        ds_elements = ds.dir()
        if csa is not None:
            csa_elements = list(csa.keys())
            all_elements = ds_elements + csa_elements
        else:
            all_elements = ds_elements
        ds_csa = {}
        ds_csa = ds_csa.fromkeys(all_elements)

        # loop through the ds/csa elements, and obtain the values
        for this_element in ds_elements:
            ds_csa[this_element] = ds[this_element].value
        if csa is not None:
            for this_element in csa_elements:
                ds_csa[this_element] = csa[this_element]

        
        # read in key_dicom_tags.txt, and get values for the most important tags
        ds_csa_key = {}
        VXD_HOME = get_vxd_home()
        if VXD_HOME is None:
            print('Error: Un-able to locate key_dicom_tags.txt file, as VXD_HOME env not specified')
            sys.exit(1)
        else:
            key_tags_file = os.path.join(VXD_HOME, 'vxdDicom', 'key_dicom_tags.txt')
        with open(key_tags_file) as f:
            key_dcm_tags = [line.rstrip() for line in f]
        for this_tag in key_dcm_tags:
            if this_tag in ds_csa:
                ds_csa_key[this_tag] = ds_csa[this_tag]
            else:
                ds_csa_key[this_tag] = ' Unspecified'
        f.close()

    return ds_csa, ds_csa_key