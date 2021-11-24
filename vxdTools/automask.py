import nibabel
import nipype.interfaces.fsl as fsl
import os
import ntpath

def automask(niiFile, deleteFiles=False, betfrac=0.4):

    # check FSL is set up first
    fsl.FSLCommand.set_default_output_type('NIFTI_GZ')
    if 'FSLDIR' not in os.environ:
        raise Exception("FSL must be installed and FSLDIR environment variable must be defined.")

    niiFolder, niiFileName = ntpath.split(niiFile)
    outFile = os.path.join(niiFolder, 'M0brain.nii.gz')
    maskFile = os.path.join(niiFolder, 'M0brain_mask.nii.gz')

    """function to create a brain mask from a nifti file, by calling FSL's BET function"""
    bet = fsl.BET()
    bet.inputs.in_file = niiFile
    bet.inputs.out_file = outFile
    bet.inputs.mask = True
    bet.inputs.frac = betfrac
    #bet.inputs.no_output = True
    bet.run()

    # load in the newly created mask, and return this
    nii = nibabel.load(maskFile)
    mask = nii.get_fdata()

    if deleteFiles:
        os.remove(outFile)
        os.remove(maskFile)

    return mask, maskFile