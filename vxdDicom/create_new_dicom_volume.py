import numpy as np
import numpy.linalg as npl
import pydicom
from pydicom.datadict import dictionary_VR
from pydicom.pixel_data_handlers.util import pixel_dtype
from pydicom.uid import ExplicitVRLittleEndian
import os
import ntpath
from vxdTools.adapt_dicom_uid import adapt_dicom_uid
from vxdTools.tidyAndNormalize import tidyAndNormalize
from vxdTools.array_to_rgb import array_to_rgb
from datetime import datetime
import sys


default_SeriesDescription = 'vxdDicom'
rgb_scaling = 255 # DICOM RGB data is usually 8 bit
# Tidy and Normalize default values
uthr_prc = 99.9
lthr_prc = 0.1
normalize = False
remove_zeros = True

valid_cmaps = ['viridis', 'plasma', 'inferno', 'magma', 'cividis',
               'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
               'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
               'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn',
               'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
               'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
               'hot', 'afmhot', 'gist_heat', 'copper',
               'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
               'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic',
               'twilight', 'twilight_shifted', 'hsv',
               'Pastel1', 'Pastel2', 'Paired', 'Accent',
               'Dark2', 'Set1', 'Set2', 'Set3',
               'tab10', 'tab20', 'tab20b', 'tab20c',
               'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
               'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg',
               'gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar']


def create_new_dicom_volume(dcm=None, nii=None, outFolder=None, colormap=None, newDcmTags=None):

    if colormap is not None:
        # check the user has passed a recognized colormap
        if any(colormap.lower() in x.lower() for x in valid_cmaps):
            rgb_flag = True
        else:
            print('Error: User-specified colormap %s not recognized' % colormap)
            return 1
    else:
        rgb_flag = False

    if dcm is None:
        print('Error: a valid dcm instance must be passed')
        return 1

    # First check to see if we are creating a new DICOM series from the data in the source dicom (i.e. just applying a
    # new colormap), or creating a new DICOM series from data contained in a NIFTI file

    if nii is not None:
        # load the nii data array
        nii_dat = nii.get_fdata()
        # remove outliers
        nii_dat = tidyAndNormalize(nii_dat, normalize=normalize, remove_zeros=remove_zeros, uthr_prc=uthr_prc, lthr_prc=lthr_prc)
        dat_out_maxval = nii_dat.max()
        dat_out_minval = nii_dat.min()

        # if the nifti data is 4D, the 4th dimension gives RGB values (this is checked by the parent function)
        if nii.ndim == 4:
            rgb_flag = True
            # if we have RGB nifti data, re-scale the RGB values to range from 0 to rgb_scaling
            nii_dat_rgb_rescaled = np.interp(nii_dat, (dat_out_minval, dat_out_maxval), (0, rgb_scaling))
            dat_out_maxval = nii_dat_rgb_rescaled.max()
            dat_out_minval = nii_dat_rgb_rescaled.min()
        else:
            # the other option is that the input data is 3D and greyscale, but the user has requested a colormap for the output
            if rgb_flag:
                # convert the data to RGB colour values
                nii_dat_rgb_rescaled = array_to_rgb(nii_dat, colormap=colormap, scaling=rgb_scaling)
                dat_out_maxval = nii_dat_rgb_rescaled.max()
                dat_out_minval = nii_dat_rgb_rescaled.min()

        """
        We now need to match the NIFTI voxels to the DICOM voxels.
        For NIFTI, the 'affine' property is the affine array relating array coordinates from the image data array to coordinates in some RAS+ 
        world coordinate system. Nibabel images always use RAS+ output coordinates.
    
        For DICOM, the LPS+ co-ordinate system is used * note this is related to the patient, not necessarily the scanner *
    
        DICOM:
        x-axis: subject's right -> subject's left
        y-axis: anterior -> posterior
        z-axis: inferior -> superior
        NIFTI:
        x-axis: left -> right
        y-axis: posterior -> anterior
        z-axis: inferior -> superior
    
        To make the nifti affine matrix compatible with dicom orientations, we need to multiply the first two rows * -1, 
        to reflect the LPS/RAS mismatch. 
        See https://discovery.ucl.ac.uk/id/eprint/1495621/1/Li%20et%20al%20The%20first%20step%20for%20neuroimaging%20data%20analysis%20-%20DICOM%20to%20NIfTI%20conversion.pdf
        """
        # Define the DICOM compatible nifti affine
        Mn = np.zeros((4, 4))
        Mn[0, :] = -nii.affine[0, :]
        Mn[1, :] = -nii.affine[1, :]
        Mn[2:, :] = nii.affine[2:, :]
        # get the inverse of this - for translating mm to indicies
        Mn_inv = npl.inv(Mn)

        if rgb_flag:
            dcm_img_from_nii = np.zeros((dcm.nRows, dcm.nCols, dcm.nSlices, 3))
        else:
            dcm_img_from_nii = np.zeros((dcm.nRows, dcm.nCols, dcm.nSlices))

    else:
        # The alternative is that we are creating a new DICOM series using the source data from the template file.
        # Remove outliers
        dat0 = tidyAndNormalize(dcm.img, normalize=normalize, remove_zeros=remove_zeros, uthr_prc=uthr_prc, lthr_prc=lthr_prc)
        if rgb_flag:
            # Convert the dicom volume data to RGB colour values
            dcm_source_dat = array_to_rgb(dat0, colormap=colormap, scaling=rgb_scaling)
        else:
            dcm_source_dat = dat0

        dat_out_maxval = dcm_source_dat.max()
        dat_out_minval = dcm_source_dat.min()

    # Loop through each DICOM file in the volume, replace the pixel array data, and update the dicom tags, before writing
    for k in range(dcm.nSlices):

        thisFile = dcm.dcmFiles[k]  # files in dcm are sorted in increasing slice order

        if not os.path.exists(outFolder):
            os.mkdir(outFolder)

        # read in the source Dicom File
        ds = pydicom.dcmread(thisFile)

        if nii is not None:
            # extract the data for this slice from the nifti array, by finding the voxel in the nifti array that matches
            # the dicom voxel's spatial co-ordinates

            for i in range(dcm.nRows):
                for j in range(dcm.nCols):

                    # get dicom voxel location in mm
                    dcm_voxel_mm = dcm.Md.dot(np.array((i, j, k, 1)))
                    # apply the inverse of the nii matrix, to go from mm to voxel indicies in the nifti dataset
                    nii_voxel_inds = Mn_inv.dot(dcm_voxel_mm)

                    # use this voxel from the nii dataset to build a new dicom slice
                    if not rgb_flag:
                        dcm_img_from_nii[i, j, k] = nii_dat[round(nii_voxel_inds[0]), round(nii_voxel_inds[1]), round(nii_voxel_inds[2])]
                        nii_thisSlice = dcm_img_from_nii[:, :, k]
                    else:
                        dcm_img_from_nii[i, j, k, :] = nii_dat_rgb_rescaled[round(nii_voxel_inds[0]), round(nii_voxel_inds[1]), round(nii_voxel_inds[2]), :]
                        nii_thisSlice = dcm_img_from_nii[:, :, k, :]

            dat_out_raw = nii_thisSlice
        else:
            if colormap is None:
                dat_out_raw = dcm_source_dat[:, :, k]
            else:
                dat_out_raw = dcm_source_dat[:, :, k, :]

        # set the output data to the appropriate format
        if not rgb_flag:
            # Greyscale data
            if nii is None:
                dat_out = dat_out_raw.astype(pixel_dtype(ds))
            else:
                dat_out = dat_out_raw.astype(np.uint16)
                ds.HighBit = 15
                ds.BitsStored = 16
                ds.BitsAllocated = 16
        else:
            # RGB data
            dat_out = dat_out_raw.astype(np.uint8)
            ds.HighBit = 7
            ds.BitsStored = 8
            ds.BitsAllocated = 8


        # -- Set the user-requested DICOM tags ----
        if newDcmTags is not None:
            if not isinstance(newDcmTags, dict):
                print('Error: newDcmTags must be a dictionary')
                return 1
            else:
                for tag in newDcmTags:
                    if tag in ds:
                        ds[tag].value = newDcmTags[tag]
                    else:
                        # create this tag if it doesn't exist
                        # first check the keyword is recognized
                        targetTag = pydicom.datadict.tag_for_keyword(tag)
                        if targetTag is not None:
                            ds.add_new(targetTag, dictionary_VR(targetTag), newDcmTags[tag])
                        else:
                            print('Warning: %s was not added, as DICOM tag not recognized' % tag)


        # --- Set the required DICOM tags for this function ---

        ds.PixelData = dat_out.tobytes()

        if rgb_flag:
            # set RGB related DICOM tags
            if 'SamplesPerPixel' in ds:
                ds.SamplesPerPixel = 3
            if 'PhotometricInterpretation' in ds:
                ds.PhotometricInterpretation = 'RGB'
            # set the Planar Configuration (0028,0006) tag, which probably won't exist yet if Samples per Pixel was 1
            if 'PlanarConfiguration' in ds:
                ds.PlanarConfiguration = 0  # order of the pixel values encoded shall be R1, G1, B1, R2, G2, B2, etc
            else:
                ds.add_new([0x0028, 0x0006], dictionary_VR([0x0028, 0x0006]), 0)

        else:
            # set greyscale related DICOM tags
            if 'SamplesPerPixel' in ds:
                ds.SamplesPerPixel = 1
            if 'PhotometricInterpretation' in ds:
                ds.PhotometricInterpretation = 'MONOCHROME2'

        if 'ImageType' in ds:
            if len(ds.ImageType) > 0:
                ds.ImageType[0] = 'DERIVED'

        currentDate = datetime.today().strftime('%Y%m%d')
        currentTime = datetime.today().strftime('%H%M%S')
        if 'InstanceCreationDate' in ds:
            ds.InstanceCreationDate = currentDate
        if 'InstanceCreationTime' in ds:
            ds.InstanceCreationTime = currentTime + '.000000'

        # create a new SOPInstanceUID
        if 'SOPInstanceUID' in ds:
            uid = ds.SOPInstanceUID
            ds.SOPInstanceUID = adapt_dicom_uid(uid)

        if 'Manufacturer' in ds:
            ds.Manufacturer = 'VoxelDesk'
        if 'ManufacturerModelName' in ds:
            ds.ManufacturerModelName = 'VoxelDesk'

        if nii is not None or rgb_flag:
            if 'WindowCenter' in ds:
                ds.WindowCenter = int(dat_out_maxval / 2)
            if 'WindowWidth' in ds:
                ds.WindowWidth = int(dat_out_maxval)
            if 'RescaleSlope' in ds:
                ds.RescaleSlope = 1
                ds.RescaleIntercept = 0

        # check if user hasn't supplied a few key tags. If so, set default values
        if not any('SeriesDescription'.lower() in x.lower() for x in newDcmTags.keys()):
            if 'SeriesDescription' in ds:
                ds.SeriesDescription = default_SeriesDescription
            else:
                targetTag = pydicom.datadict.tag_for_keyword('SeriesDescription')
                if targetTag is not None:
                    ds.add_new(targetTag, dictionary_VR(targetTag), default_SeriesDescription)
                else:
                    print('Warning: %s was not added, as DICOM tag not recognized' % targetTag)
            newDcmTags['SeriesDescription'] = ds.SeriesDescription

        if not any('LargestImagePixelValue'.lower() in x.lower() for x in newDcmTags.keys()):
            if 'LargestImagePixelValue' in ds:
                ds.LargestImagePixelValue = int(dat_out.max())
            else:
                targetTag = pydicom.datadict.tag_for_keyword('LargestImagePixelValue')
                if targetTag is not None:
                    ds.add_new(targetTag, dictionary_VR(targetTag), dat_out.max())
                else:
                    print('Warning: %s was not added, as DICOM tag not recognized' % targetTag)

        if not any('SmallestImagePixelValue'.lower() in x.lower() for x in newDcmTags.keys()):
            if 'SmallestImagePixelValue' in ds:
                ds.SmallestImagePixelValue = int(dat_out.min())
            else:
                targetTag = pydicom.datadict.tag_for_keyword('SmallestImagePixelValue')
                if targetTag is not None:
                    ds.add_new(targetTag, dictionary_VR(targetTag), dat_out.min())
                else:
                    print('Warning: %s was not added, as DICOM tag not recognized' % targetTag)

        # Write out the new DICOM File. Use first file = 1 (rather than 0)
        if k + 1 < 10:
            kstr = '00' + str(k + 1)
        if k + 1 >= 10 and k + 1 < 100:
            kstr = '0' + str(k + 1)
        if k + 1 >= 100:
            kstr = str(k + 1)

        outFileName = newDcmTags['SeriesDescription'] + '-' + kstr + '.dcm'
        outFilePath = os.path.join(outFolder, outFileName)

        # DICOMs pulled from PACS via Osirix may use a compressed transfer syntax, giving the pixel data an undefined length.
        # This can cause an error when writing the new DICOMs
        if ds['PixelData'].is_undefined_length:
            #ds.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian # pydicom will set the is_undefined_length flag automatically to match the transfer syntax when writing to file.
            # switching to method used by dicomsort.py
            ds.decompress()


        ds.save_as(outFilePath)




