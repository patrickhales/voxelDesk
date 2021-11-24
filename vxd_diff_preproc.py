#!/usr/bin/env python

"""
Program to perform the following pre-processing steps of raw dMRI data (for mrtrix tractography)
- denoising
- remove Gibbs ringing
- eddy and topup
- brain masking
- DTI calculations
- CSD pre-processing
- whole-brain tractography
"""
import ntpath
import os
import subprocess
import nibabel
import argparse
import sys
import time
import shutil
import nipype.interfaces.mrtrix3 as mrt
from vxdDiff.dwi_preproc_info_from_nii import dwi_preproc_info_from_nii
from vxdDiff.dwi_preproc_from_json import dwi_preproc_from_json
from termcolor import colored

if __name__ == '__main__':

    print(' ')
    rawdata = None
    b0negPEdata = None
    denoise = True
    degibbs = True
    eddy = True
    topup = False       # only set to True if b0flip data is supplied
    wholebrain = True   # flag for running whole brain tractography

    # Construct the argument parser
    ap = argparse.ArgumentParser(add_help=False)

    # Add the arguments to the parser

    required = ap.add_argument_group('required arguments')
    optional = ap.add_argument_group('optional arguments')

    required.add_argument("-i", "--input", required=True, help="Input Raw data (DICOM folder or NIFTI file)")
    optional.add_argument("-f", "--b0flip", required=False, help="B0 flip DICOM folder or NIFTI file")
    optional.add_argument("-m", "--mask", required=False, help="Brain mask (nii/mif file - over-rides auto-masking")
    optional.add_argument("-p", "--pedir", required=False, help="Phase encoding direction (raw data)")
    optional.add_argument("-xe", "--noeddy", required=False, action='store_true', help="Skip eddy correction stage")
    optional.add_argument("-xt", "--notract", required=False, action='store_true', help="Skip wholebrain tractography stage")
    optional.add_argument('-h', '--help', action='help', help='Show this help message and exit')

    args = ap.parse_args()

    print(' ')
    print(colored('*** Starting voxelDesk diffusion preprocessing... ***', 'green'))
    print(' ')
    start_time = time.time()

    # Define output folder
    wdir = os.getcwd()
    outFolder = os.path.join(wdir, 'vxd_mrtrix')
    if not os.path.exists(outFolder):
        os.mkdir(outFolder)

    # Raw data dicom folder / nifti file
    rawdata = args.input
    # check if user has passed full path or relative path to the raw data
    if not os.path.isabs(rawdata):
        wdir = os.getcwd()
        rawdata = os.path.join(wdir, rawdata)


    # check if wholebrain tractography stage has been requested to be skipped
    if args.notract:
        wholebrain = False

    # b0flip dicom folder / nifti file
    if args.b0flip:
        topup = True
        b0negPEdata = args.b0flip
        if not os.path.isabs(b0negPEdata):
            wdir = os.getcwd()
            b0negPEdata = os.path.join(wdir, b0negPEdata)
    else:
        print(' ')
        print(colored('- No b0 flip data provided. Topup will not be run...', 'magenta'))
        print(' ')

    # Check if user has requested the eddy stage be skipped.
    if args.noeddy:
        eddy = False
        print(' ')
        print(colored('- Eddy / top-up correction will be skipped...', 'magenta'))

    # Check if user has passed a PE direction, otherwise AP will be assumed for now (the final dwi_raw.mif will later be checked for this info)
    pedir_user = None
    pedir_options = ['-0', '+0', '-1', '+1', '-2', '+2', 'lr', 'rl', 'pa', 'ap', 'is', 'si', 'i-', 'i+', 'j-', 'j+', 'k-', 'k+']
    if args.pedir:
        pedir_user = args.pedir
        # check if user pe direction is valid
        if any(pedir_user.lower() in x.lower() for x in pedir_options):
            pedir = pedir_user.lower()
        else:
            print(colored(f'Error: User-specified PE direction {pedir_user} not recognized', 'red'))
            sys.exit()
    else:
        pedir = 'AP'

    rawdataParent, rawdataChild = ntpath.split(rawdata)

    # check if user has passed full path or relative path to the raw data
    if not os.path.isabs(rawdata):
        wdir = os.getcwd()
        rawdata = os.path.join(wdir, rawdata)
    if b0negPEdata is not None:
        if not os.path.isabs(b0negPEdata):
            wdir = os.getcwd()
            b0negPEdata = os.path.join(wdir, b0negPEdata)

    # First find out if the user has passed the raw data as a nifti file, or dicom folder
    # Check if the rawdata looks like a NIFTI file
    if '.nii' in rawdata:
        try:
            nii = nibabel.load(rawdata)
            rawdata_is_nifti = True
            print(colored(f'- Raw data NIFTI file:\t{rawdata}', 'green'))
        except Exception:
            print(colored(f'Error: Raw NIFTI file cannot be read:{rawdata}', 'red'))
            sys.exit()
    else:
        rawdata_is_nifti = False

    if b0negPEdata is not None:
        if '.nii' in b0negPEdata:
            try:
                nii = nibabel.load(b0negPEdata)
                b0negPEdata_is_nifti = True
                print(colored(f'- b0 flip NIFTI file:\t{b0negPEdata}', 'green'))
            except Exception:
                print(colored(f'Error: b0negPEdata NIFTI file cannot be read: {b0negPEdata}', 'red'))
                sys.exit()
        else:
            b0negPEdata_is_nifti = False

    # if not NIFTI, see if the user has passed a DICOM folder
    if not rawdata_is_nifti:
        if not os.path.isdir(rawdata):
            print(colored('Error: raw data must be either a NIFTI file or DICOM folder', 'red'))
            sys.exit()
        else:
            print(colored(f'- Raw data DICOM folder:\t{rawdata}', 'green'))

    if b0negPEdata is not None:
        if not b0negPEdata_is_nifti:
            if not os.path.isdir(b0negPEdata):
                print(colored('Error: b0negPEdata must be either a NIFTI file or DICOM folder', 'red'))
                sys.exit()
            else:
                print(colored(f'- b0 flip DICOM folder:\t\t{b0negPEdata}', 'green'))

    if args.mask:
        userMask = True
        maskFile = args.mask
        # check if user has passed full path or relative path to the mask
        if not os.path.isabs(maskFile):
            wdir = os.getcwd()
            maskFile = os.path.join(wdir, maskFile)
        # check the mask file exists
        if not os.path.exists(maskFile):
            print(colored(f'Error: Mask File could not be found: {maskFile}', 'red'))
            sys.exit()
    else:
        userMask = False


    print(colored(f'- Output folder:\t\t{outFolder}', 'green'))
    print(' ')

    # if rawdata is a nifti file, attempt to get useful dwipreproc data from associated json side car / bvals / bvecs files
    if rawdata_is_nifti:
        dwi_preproc_from_nii = dwi_preproc_info_from_nii(rawdata)
    else:
        dwi_preproc_from_nii = None

    # write a mif version of the b0negPEdata file to the mrtrix folder
    if b0negPEdata is not None:
        print(colored('Converting b0 flip data to mif...', 'green'))
        outFile_b0negPE = os.path.join(outFolder, 'b0negPE.mif')
        subprocess.run(['mrconvert', b0negPEdata, outFile_b0negPE, '-force'])
        print(colored('...done', 'green'))
        print(' ')


    # create an mrtrix mif/json file of the raw data
    outFile_raw = os.path.join(outFolder, 'dwi_raw.mif')
    outFile_raw_json = os.path.join(outFolder, 'dwi_raw.json')
    if not rawdata_is_nifti:
        # use DICOM folder to create the mif file
        print(colored('Converting raw data to mif...', 'green'))
        subprocess.run(['mrconvert', '-json_export', outFile_raw_json, rawdata, outFile_raw, '-force'])
        print(colored('...done', 'green'))
        print(' ')
    else:
        # use NIFTI data to create the mif file
        mrconvert_str = ['mrconvert', '-json_export', outFile_raw_json]

        if dwi_preproc_from_nii.bvalFile is not None and dwi_preproc_from_nii.bvecFile is not None:
            mrconvert_str.extend(['-fslgrad', dwi_preproc_from_nii.bvecFile, dwi_preproc_from_nii.bvalFile])

        if dwi_preproc_from_nii.jsonFile is not None:
            mrconvert_str.extend(['-json_import', dwi_preproc_from_nii.jsonFile])

        mrconvert_str.extend([rawdata, outFile_raw, '-force'])
        print('Converting raw data to mif...')
        subprocess.run(mrconvert_str)
        print(colored('...done', 'green'))
        print(' ')

    # We've now created a mif/json file of the raw data. Use the json file to recap what info we know at this stage
    dwi_preproc = dwi_preproc_from_json(outFile_raw_json)
    if pedir_user is not None:
        dwi_preproc.PhaseEncodingDirection = pedir_user.lower()
    else:
        dwi_preproc.PhaseEncodingDirection = pedir
        print(colored(f'Found PE direction from data: PE = {dwi_preproc.PhaseEncodingDirection}', 'magenta'))
        print(' ')
        print(colored('Diffusion shells: ', 'magenta'))
        for b in range(dwi_preproc.shells):
            print(colored(f'b = {dwi_preproc.shell_bvals[b]} s/mm2, vols = {dwi_preproc.shell_vols[b]}', 'magenta'))

        # Determine if data is multi-shell
        if dwi_preproc.shells > 2:
            dwi_preproc.multiShell = True
            print(colored('Multi-shell data detected', 'magenta'))
        else:
            dwi_preproc.multiShell = False
            print(colored('Single-shell data detected', 'magenta'))
        print(' ')

    # extract all the b0 volumes
    print(colored('Extracting b0 volumes...', 'green'))
    outFile_b0all = os.path.join(outFolder, 'b0all.mif')
    subprocess.run(['dwiextract', '-bzero', outFile_raw, outFile_b0all, '-force'])
    print(colored('...done', 'green'))
    print(' ')

    # extract the first b0 volume
    print(colored('Extracting first b0 volume...', 'green'))
    outFile_b0 = os.path.join(outFolder, 'b0.mif')
    subprocess.run(['mrconvert', outFile_b0all, '-coord', '3', '0', '-axes', '0,1,2', outFile_b0, '-force'])
    print(colored('...done', 'green'))
    print(' ')

    # create a b0mean image
    print(colored('Creating mean b0 image...', 'green'))
    outFile_b0mean = os.path.join(outFolder, 'b0mean.mif')
    subprocess.run(['mrmath', outFile_b0all, 'mean', outFile_b0mean, '-axis', '3', '-force'])
    print(colored('...done', 'green'))
    print(' ')

    # If we have a b0negPE.mif file, create the b0pair file, by merging it with the first b0 volume from the raw data
    if topup:
        outFile_b0pair = os.path.join(outFolder, 'b0pair.mif')
        print(colored('Concatenating b0 and b0negPE volumes...', 'green'))
        subprocess.run(['mrcat', outFile_b0, outFile_b0negPE, outFile_b0pair, '-force'])
        dwi_preproc.b0pairFile = outFile_b0pair
        print(colored('...done', 'green'))
        print(' ')
    else:
        dwi_preproc.b0pairFile = None

    currentFile = outFile_raw

    # Denoise the raw data (note - this must be the first step, as it needs to work on raw (un-smoothed) data
    if denoise:
        outFile_denoised = os.path.join(outFolder, 'dwi_denoised.mif')
        outFile_sigma = os.path.join(outFolder, 'noise_sigma.mif')
        print(colored('Denoising raw data...', 'green'))
        subprocess.run(['dwidenoise', '-noise', outFile_sigma, currentFile, outFile_denoised, '-force'])
        print(colored('...done', 'green'))
        print(' ')
        currentFile = outFile_denoised

    # Run Gibbs ringing removal
    if degibbs:
        outFile_unringed = os.path.join(outFolder, 'dwi_unringed.mif')
        print(colored('Performing Gibbs ringing removal...', 'green'))
        subprocess.run(['mrdegibbs', currentFile, outFile_unringed, '-force'])
        print(colored('...done', 'green'))
        print(' ')
        currentFile = outFile_unringed

    # Run topup / eddy
    dwi_preproc.preprocFile = os.path.join(outFolder, 'dwi_preproc.mif')
    if eddy:
        if topup:
            print(colored('Running topup and eddy...', 'green'))
            subprocess.run(['dwifslpreproc', currentFile, dwi_preproc.preprocFile, '-rpe_pair', '-se_epi', dwi_preproc.b0pairFile,
                            '-pe_dir', dwi_preproc.PhaseEncodingDirection, '-align_seepi', '-force'])
            print(colored('...done', 'green'))
            print(' ')
        else:
            print(colored('Running eddy (without topup)...', 'green'))
            subprocess.run(['dwifslpreproc', currentFile, dwi_preproc.preprocFile, '-rpe_none', '-pe_dir', dwi_preproc.PhaseEncodingDirection, '-force'])
            print(colored('...done', 'green'))
            print(' ')
    else:
        shutil.copyfile(currentFile, dwi_preproc.preprocFile)
        print(colored('Eddy / Topup stage skipped...', 'magenta'))
        print(' ')

    # Re-calculate a b0mean image, using the top/eddy-corrected b0s
    # extract all the b0 volumes
    if eddy or topup:
        print(colored('Extracting corrected b0 volumes from topup/eddy data...', 'green'))
        outFile_b0all = os.path.join(outFolder, 'b0all.mif')
        subprocess.run(['dwiextract', '-bzero', dwi_preproc.preprocFile, outFile_b0all, '-force'])
        print(colored('...done', 'green'))
        print(' ')

        # create a b0mean image
        print(colored('Creating corrected mean b0 image from topup/eddy b0s...', 'green'))
        outFile_b0mean = os.path.join(outFolder, 'b0mean.mif')
        subprocess.run(['mrmath', outFile_b0all, 'mean', outFile_b0mean, '-axis', '3', '-force'])
        print(colored('...done', 'green'))
        print(' ')

    # Create brain mask, if not supplied by user (Check this!)
    if not userMask:
        dwi_preproc.maskFile = os.path.join(outFolder, 'mask.mif')
        print(colored('Creating brain mask...', 'green'))
        subprocess.run(['dwi2mask', dwi_preproc.preprocFile, dwi_preproc.maskFile, '-force'])
        print(colored('...done', 'green'))
        print(' ')
    else:
        print(colored(f'Using user-supplied mask: {maskFile}', 'green'))
        dwi_preproc.maskFile = maskFile

    # erode the mask, to exclude high-FA voxels at the periphery
    dwi_preproc.maskFileEroded = os.path.join(outFolder, 'mask_eroded.mif')
    print(colored('Eroding brain mask...', 'green'))
    subprocess.run(['maskfilter', '-npass', '3', dwi_preproc.maskFile, dwi_preproc.maskFileEroded, '-force'])

    # Tensor calculations
    print(colored('Calculating diffusion tensor...', 'green'))
    dwi_preproc.tensorFile = os.path.join(outFolder, 'dt.mif')
    subprocess.run(['dwi2tensor', dwi_preproc.preprocFile, dwi_preproc.tensorFile, '-force'])

    # Create masked versions of the DTI maps
    dwi_preproc.adcFile = os.path.join(outFolder, 'adc.mif')
    dwi_preproc.faFile = os.path.join(outFolder, 'fa.mif')
    dwi_preproc.evFile = os.path.join(outFolder, 'ev.mif')
    subprocess.run(['tensor2metric', '-adc', dwi_preproc.adcFile, '-fa', dwi_preproc.faFile, '-vector', dwi_preproc.evFile,
                    '-mask', dwi_preproc.maskFile, dwi_preproc.tensorFile, '-force'])
    print(colored('...done', 'green'))
    print(' ')

    # Calculate the single-fibre response function. Use the eroded brain mask for this
    print(colored('Calculating CSD response functions...', 'green'))
    dwi_preproc.wmResponseFile = os.path.join(outFolder, 'wm_response.txt')
    dwi_preproc.gmResponseFile = os.path.join(outFolder, 'gm_response.txt')
    dwi_preproc.csfResponseFile = os.path.join(outFolder, 'csf_response.txt')
    dwi_preproc.responseVoxelsFile = os.path.join(outFolder, 'response_voxels.mif')
    if dwi_preproc.multiShell:
        print(colored('Using dhollander method for multi-shell data...', 'magenta'))
        subprocess.run(['dwi2response', 'dhollander', dwi_preproc.preprocFile, dwi_preproc.wmResponseFile,
                    dwi_preproc.gmResponseFile, dwi_preproc.csfResponseFile, '-voxels',
                    '-mask', dwi_preproc.maskFileEroded, dwi_preproc.responseVoxelsFile, '-force'])
    else:
        print(colored('Using tournier method for single-shell data...', 'magenta'))
        subprocess.run(['dwi2response', 'tournier', dwi_preproc.preprocFile, dwi_preproc.wmResponseFile,
                     '-voxels', dwi_preproc.responseVoxelsFile, '-mask', dwi_preproc.maskFileEroded, '-force'])
        dwi_preproc.gmResponseFile = None
        dwi_preproc.csfResponseFile = None
    print(colored('...done', 'green'))
    print(' ')

    # Perform Constrained Spherical Deconvolution (CSD) based on the response function estimated above
    print(colored('Performing CSD...', 'green'))
    if dwi_preproc.multiShell:
        print(colored('Using multi-shell, multi-tissue method...', 'magenta'))
        dwi_preproc.wmodfFile = os.path.join(outFolder, 'wmodf.mif')
        dwi_preproc.gmodfFile = os.path.join(outFolder, 'gmodf.mif')
        dwi_preproc.csfodfFile = os.path.join(outFolder, 'csfodf.mif')
        subprocess.run(['dwi2fod', 'msmt_csd', dwi_preproc.preprocFile, dwi_preproc.wmResponseFile, dwi_preproc.wmodfFile,
                        dwi_preproc.gmResponseFile, dwi_preproc.gmodfFile,
                        dwi_preproc.csfResponseFile, dwi_preproc.csfodfFile,
                        '-mask', dwi_preproc.maskFile, '-force'])
    else:
        print(colored('Using single-shell single-tissue method...', 'magenta'))
        dwi_preproc.wmodfFile = os.path.join(outFolder, 'wmodf.mif')
        dwi_preproc.gmodfFile = None
        dwi_preproc.csfodfFile = None
        subprocess.run(['dwi2fod', 'csd', dwi_preproc.preprocFile, dwi_preproc.wmResponseFile, dwi_preproc.wmodfFile,
                        '-mask', dwi_preproc.maskFile, '-force'])
    print(colored('...done', 'green'))
    print(' ')

    if wholebrain:
        # Run whole-brain tractography
        print(colored('Running whole-brain tractography...', 'green'))
        dwi_preproc.tractFolder = os.path.join(outFolder, 'rois_and_tracts')
        if not os.path.exists(dwi_preproc.tractFolder):
            os.mkdir(dwi_preproc.tractFolder)
        dwi_preproc.wholeBrainTckFile = os.path.join(dwi_preproc.tractFolder, 'wholebrain.tck')
        subprocess.run(['tckgen', dwi_preproc.wmodfFile, dwi_preproc.wholeBrainTckFile,
                        '-seed_image', dwi_preproc.maskFile, '-mask', dwi_preproc.maskFile,
                        '-select', '1M', '-force'])
        print(colored('...done', 'green'))
        print(' ')

        # Create colour Track Density Image
        print(colored('Generating colour wholebrain tractography TDI image...', 'green'))
        dwi_preproc.wholeBrainTdiFile = os.path.join(dwi_preproc.tractFolder, 'wholebrain_tdi_1mm.mif')
        subprocess.run(['tckmap', dwi_preproc.wholeBrainTckFile, dwi_preproc.wholeBrainTdiFile,
                    '-template', dwi_preproc.faFile, '-vox', '1', '-dec', '-force'])
        print(colored('...done', 'green'))
        print(' ')

        # Create greyscale Track Density Image
        print(colored('Generating greyscale wholebrain tractography TDI image...', 'green'))
        dwi_preproc.wholeBrainTdiFile = os.path.join(dwi_preproc.tractFolder, 'wholebrain_tdi_1mm_grey.mif')
        subprocess.run(['tckmap', dwi_preproc.wholeBrainTckFile, dwi_preproc.wholeBrainTdiFile,
                    '-template', dwi_preproc.faFile, '-vox', '1', '-force'])
        print(colored('...done', 'green'))
        print(' ')


    end_time = time.time()
    processing_time_min = (end_time - start_time) / 60

    print(' ')
    print(colored('*** Completed voxelDesk diffusion pre-processing... ***', 'green'))
    print(colored('Pre-processing time {processing_time_min} minutes', 'green'))
    print(' ')
    print('*** Now run post-hoc checks (from vxd_mrtrix folder) ***')
    print(' ')
    print('Run the following command to check the mask:')
    print(colored('mrview dwi_preproc.mif -roi.load mask.mif &', 'magenta'))

    print(' ')
    print('Check selected voxels for response function calculation using:')
    print(colored('mrview fa.mif -overlay.load response_voxels.mif &', 'magenta'))

    print(' ')
    print('Check the WM (and GM, CSF) response function(s) using:')
    print(colored('shview wm_response.txt &', 'magenta'))

    print(' ')
    print('Check the ODFs using:')
    print(colored('mrview fa.mif -odf.load_sh wmodf.mif &', 'magenta'))

    print(' ')
    print('Check whole-brain tractography using (from rois_and_tracts folder):')
    print(colored('mrview ../fa.mif -tractography.load wholebrain.tck &', 'magenta'))























