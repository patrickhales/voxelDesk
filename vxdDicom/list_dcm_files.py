# function to return a list of all dicom files in a given folder (or tree)

import os
import pydicom
from pydicom.filereader import InvalidDicomError

def list_dcm_files(sourceFolder):

    allFiles = []
    allDcmFiles = []
    allNonDcmFiles = []

    allSeriesInstanceUIDs = []
    allSeriesDescriptions = []
    allStudyInstanceUIDs = []
    allStudyDates = []
    allPatientNames = []
    allPatientIDs = []

    # check if user has passed an absolute or relative path
    if not os.path.isabs(sourceFolder):
        wdir = os.getcwd()
        sourceFolder = os.path.join(wdir, sourceFolder)

    # walk through the directory tree and list all the dicom / non-dicom files
    for root, subFolders, files in os.walk(sourceFolder):
        for file in files:
            file = os.path.join(root, file)
            allFiles.append(file)

            # check for dicom files
            try:
                ds = pydicom.read_file(file, stop_before_pixels=True)
                allDcmFiles.append(file)
                # get Study / Series info about this file
                if 'StudyInstanceUID' in ds:
                    allStudyInstanceUIDs.append(ds.StudyInstanceUID)
                if 'StudyDate' in ds:
                    allStudyDates.append(ds.StudyDate)
                if 'SeriesInstanceUID' in ds:
                    allSeriesInstanceUIDs.append(ds.SeriesInstanceUID)
                if 'SeriesDescription' in ds:
                    allSeriesDescriptions.append(ds.SeriesDescription)
                if 'PatientName' in ds:
                    allPatientNames.append(ds.PatientName)
                if 'PatientID' in ds:
                    allPatientIDs.append(ds.PatientID)

            except (IOError, os.error) as why:
                allNonDcmFiles.append(file)
            except InvalidDicomError:
                allNonDcmFiles.append(file)
            except KeyError:
                allNonDcmFiles.append(file)

    # determine the unique studies and series in the lists
    unique_studies = list(set(allStudyInstanceUIDs))
    unique_series = list(set(allSeriesInstanceUIDs))
    unique_study_dates = list(set(allStudyDates))
    unique_series_descriptions = list(set(allSeriesDescriptions))
    unique_patient_names = list(set(allPatientNames))
    unique_patient_ids = list(set(allPatientIDs))

    # create a dictionary with the unique study UIDs as the primary key, the unique series UIDs as the secondary,
    # and the dicom files as the values
    dcm = {}

    for thisUniqueStudy in unique_studies:
        series_dict = {}
        for thisUniqueSeries in unique_series:
            filesInSeries = []
            # loop through all dicom files
            for thisFile in allDcmFiles:
                ds = pydicom.read_file(thisFile, stop_before_pixels=True)
                if 'StudyInstanceUID' in ds:
                    thisStudyInstanceUID = ds.StudyInstanceUID
                if 'SeriesInstanceUID' in ds:
                    thisSeriesInstanceUID = ds.SeriesInstanceUID

                if thisStudyInstanceUID == thisUniqueStudy and thisSeriesInstanceUID == thisUniqueSeries:
                    filesInSeries.append(thisFile)

            # add the list of all files for this study/series to the dictionary
            series_dict[thisUniqueSeries] = filesInSeries
            dcm[thisUniqueStudy] = series_dict

    # sort the file lists
    for thisStudyKey in dcm.keys():
        for thisSeriesKey in dcm[thisStudyKey].keys():
            thisFileList = dcm[thisStudyKey][thisSeriesKey]
            dcm[thisStudyKey][thisSeriesKey] = sorted(thisFileList)

    # create a summary of the file contents
    dcm_summary = {'Study UIDs': unique_studies,
                   'Series UIDs': unique_series,
                   'Study Dates': unique_study_dates,
                   'Series Descriptions': unique_series_descriptions,
                   'Patient Names': unique_patient_names,
                   'Patient IDs': unique_patient_ids
                   }

    return dcm, dcm_summary










