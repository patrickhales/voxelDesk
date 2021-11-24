import nibabel
import numpy as np
from matplotlib import pyplot as plt
import os
from vxdTools.tidyAndNormalize import tidyAndNormalize

# TDI DEC file
#tdiFile = '/Users/halesp/experimental_results/MR6/DTI/sequence_setup/20210302_ph/vxd_mrtrix/rois_and_tracts/wholebrain_tdi_1mm.nii.gz'
#tdiFile = 'C:\\Users\\sejjph0\\experimental_results\dti\\vxd_mrtrix\\rois_and_tracts\\wholebrain_tdi_1mm.nii.gz'
#tdiFile = '/Users/patrickhales/experimental_results/test/dti/vxd_mrtrix/rois_and_tracts/wholebrain_tdi_1mm.nii.gz'
tdiFile = '/Users/patrickhales/experimental_results/test/dti/t1space_20201217/vxd_nifti/10001-t1_space_sag_p4_tr700_turbo20/wholebrain_tdi_1mm_rt1.nii.gz'

# TDI magnitude file
#tdiMagFile = 'C:\\Users\\sejjph0\\experimental_results\dti\\vxd_mrtrix\\rois_and_tracts\\wholebrain_tdi_1mm_grey.nii.gz'
#tdiMagFile = '/Users/patrickhales/experimental_results/test/dti/vxd_mrtrix/rois_and_tracts/wholebrain_tdi_1mm_grey.nii.gz'
tdiMagFile = '/Users/patrickhales/experimental_results/test/dti/t1space_20201217/vxd_nifti/10001-t1_space_sag_p4_tr700_turbo20/wholebrain_tdi_1mm_rt1_grey.nii.gz'

#outFolder = '/Users/halesp/experimental_results/MR6/DTI/sequence_setup/20210302_ph/vxd_mrtrix/rois_and_tracts/tdi_tests/'
#outFolder = 'C:\\Users\\sejjph0\\experimental_results\dti\\vxd_mrtrix\\rois_and_tracts\\tdi_tests'
#outFolder = '/Users/patrickhales/experimental_results/test/dti/vxd_mrtrix/rois_and_tracts/tdi_tests/'
outFolder = '/Users/patrickhales/experimental_results/test/dti/t1space_20201217/vxd_nifti/10001-t1_space_sag_p4_tr700_turbo20/'

# load the RGB TDI DEC data
nii = nibabel.load(tdiFile)
dec = nii.get_fdata()

# load the magnitude TFI data
nii2 = nibabel.load(tdiMagFile)
mag = nii2.get_fdata()

# calc the sum of the RGB values in each voxel
dec_sum = dec.sum(axis=3)
dec_max = dec.max(axis=3)
dec_min = dec.min(axis=3)

mag_filt = tidyAndNormalize(mag, normalize=False, remove_zeros=True, uthr_prc=99.5, lthr_prc=0)

dec_sum_norm = tidyAndNormalize(dec_sum, normalize=True, remove_zeros=True, uthr_prc=99.9, lthr_prc=0.01)
dec_max_norm = tidyAndNormalize(dec_max, normalize=True, remove_zeros=True, uthr_prc=99.9, lthr_prc=0.01)
mag_norm = tidyAndNormalize(mag_filt, normalize=True, remove_zeros=True, uthr_prc=100, lthr_prc=0)

# Normalize the RGB values to range from 0 to 1 in each voxel, if not already done so
# (note vecreg normalizes the RGB values for you)
if dec_max.max() > 1.0:
    dec_norm = np.zeros(dec.shape)
    for i in range(3):
        dec_norm[:, :, :, i] = dec[:, :, :, i] / mag_filt
    dec_norm[np.isnan(dec_norm)] = 0
    dec_norm[np.isinf(dec_norm)] = 0
else:
    dec_norm = dec

# modulate the normalized RGB values by the normalized dec_sum
dec_norm_mod = np.zeros(dec.shape)
for i in range(3):
    #dec_norm_mod[:, :, :, i] = dec_norm[:, :, :, i] * dec_sum_norm
    dec_norm_mod[:, :, :, i] = dec_norm[:, :, :, i] * mag_norm

# write out the dec_norm_mod file
outFile = os.path.join(outFolder, 'dec_norm_mod.nii.gz')
nibabel.save(nibabel.Nifti1Image(dec_norm_mod, nii.affine, nii.header), outFile)
