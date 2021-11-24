# function to summarize key metrics for a given dicom series
# pass a list of dicom series files, which should all be from the same series (use list_dcm_files.py for this)

import pydicom
import numpy as np

def summarize_dcm_series(templateSeriesFiles):

    noSeriesFiles = len(templateSeriesFiles)
    maxPixelVals = np.full(noSeriesFiles, np.nan)
    minPixelVals = np.full(noSeriesFiles, np.nan)
    sliceLocations = np.full(noSeriesFiles, np.nan)
    imagePositionPatient = np.full([noSeriesFiles, 3], np.nan)

    # loop through the templateSeriesFiles and extract the metrics
    for fctr, thisFile in enumerate(templateSeriesFiles):
        ds = pydicom.dcmread(thisFile)
        if 'LargestImagePixelValue' in ds:
            maxPixelVals[fctr] = ds.LargestImagePixelValue
        if 'SmallestImagePixelValue' in ds:
            minPixelVals[fctr] = ds.SmallestImagePixelValue
        if 'SliceLocation' in ds:
            sliceLocations[fctr] = ds.SliceLocation
        if 'ImagePositionPatient' in ds:
            imagePositionPatient[fctr, :] = ds.ImagePositionPatient

    # loop through the imagePositionPatient vectors, and count the number of unique values. This should tell us the number
    # of unique slices. Note if two slices match, the no unique slices will be 2 lower than expected no slices, as 2 slices
    # are not unique
    unique_slice_ctr = 0

    for pctr, thisPosition in enumerate(imagePositionPatient):
        # create a version imagePositionPatient excluding this entry
        remainingImagePositions = imagePositionPatient.copy()
        remainingImagePositions = np.delete(remainingImagePositions, pctr, 0)
        # see if this entry exists again in the remain image positions
        thisEntryDuplicateCtr = 0
        for compValue in remainingImagePositions:
            if thisPosition[0] == compValue[0] and thisPosition[1] == compValue[1] and thisPosition[2] == compValue[2]:
                thisEntryDuplicateCtr += 1
        # if no duplicates have been found, increment the unique slice ctr
        if thisEntryDuplicateCtr == 0:
            unique_slice_ctr += 1

    # summarize the data
    maxSeriesPixelValue = int(np.nanmax(maxPixelVals))
    minSeriesPixelValue = int(np.nanmin(minPixelVals))

    series_summary = {'maxSeriesPixelValue': maxSeriesPixelValue,
                      'minSeriesPixelValue': minSeriesPixelValue,
                      'no dcm files': noSeriesFiles,
                      'no unique slices': unique_slice_ctr,
                      'maxPixelVals': maxPixelVals,
                      'minPixelVals': minPixelVals,
                      'slice locations': sliceLocations,
                      'ImagePositionPatient': imagePositionPatient
                      }

    return series_summary




