# function to tidy a numpy array (remove NaNs/Infs), clip outliers, and normalize

import numpy as np

def tidyAndNormalize(dat, normalize=False, remove_zeros=False, uthr_prc=99.9, lthr_prc=0.1):
    dat[np.isnan(dat)] = 0.0
    dat[np.isinf(dat)] = 0.0
    if remove_zeros:
        dat[dat < 0] = 0
    dat_vec = dat.flatten()
    uthr = np.percentile(dat_vec, uthr_prc)
    lthr = np.percentile(dat_vec, lthr_prc)
    dat = np.clip(dat, a_min=lthr, a_max=uthr)
    if normalize:
        dat = (dat - lthr) / (uthr - lthr)  # normalise intensities between 0 - 1
    dat[np.isnan(dat)] = 0.0
    dat[np.isinf(dat)] = 0.0
    return dat
