import os
from deid.dicom.parser import DicomParser
from vxdSort.dicomTree import dTree
from vxdTools.readConfigFile import readConfigFile

def anonymize(dicomFolder=None, sorter=None, patientIDs=None):

    # load the default parameters from the config file
    config = readConfigFile()

    dicomOutputFolderBase = dicomFolder
    sortedDicomFolder = os.path.join(dicomOutputFolderBase, config['sortedDicomFolderName'])

    # use the sorter object to create the dicomTree
    dt = dTree(sorter)

    # see how many patients are in the root Dicom folder
    npatients = len(dt.patients)

    if patientIDs is None:
        patientIDs = []
        for pctr, patient in enumerate(dt.patients):
            if pctr < 10:
                thisPatientID = 'vxdAnon-000' + str(pctr)
            else:
                if pctr < 100:
                    thisPatientID = '00' + str(pctr)
                else:
                    thisPatientID = '0' + str(pctr)
            print('')
            print('Coding Patient %s (%s) as: %s' % (pctr+1, patient, thisPatientID))
            patientIDs.append(thisPatientID)
    else:
        if len(patientIDs) != npatients:
            print('Error: Supplied patientIDs list has %s item(s), but Dicom root folder contains %s patients'
                  % (str(len(patientIDs)), str(npatients)))
            return 1
        else:
            for pctr, patient in enumerate(dt.patients):
                print('')
                print('Coding Patient %s (%s) as: %s' % (pctr + 1, patient, patientIDs[pctr]))


    # create a dictionary to link patient IDs and patient names
    patientLookup = {}
    for pctr, patientID in enumerate(patientIDs):
        patientLookup[patientID] = dt.patients[pctr]

    # create the target anonymized folder structure
    sortedDicomFolderAnon = os.path.join(dicomOutputFolderBase, config['sortedDicomFolderName'] + '_anon')
    if not os.path.exists(sortedDicomFolderAnon):
        os.makedirs(sortedDicomFolderAnon)

    # iterate through each patient
    for pctr, patient in enumerate(dt.patients):
        patientFolderSource = patient
        patientFolderSourceFull = os.path.join(sortedDicomFolder, patientFolderSource)
        patientFolderTarget = patientIDs[pctr]
        patientFolderTargetFull = os.path.join(sortedDicomFolderAnon, patientFolderTarget)
        if not os.path.exists(patientFolderTargetFull):
            os.makedirs(patientFolderTargetFull)

        studyBranch = dt.tree[patient]  # list of the all the studies for this patient
        # for this patient, iterate through all studies
        for studyctr, study in enumerate(studyBranch):
            seriesBranch = studyBranch[study]  # list of the all the series for this study
            # for this study, iterate through all series
            print('')
            print('Anonymizing %s, study %s...' % (patient, study))
            for seriesctr, series in enumerate(seriesBranch):
                filesBranch = seriesBranch[series] # list of the all the files for this series

                # piece together the full source / target folder names
                seriesSourceFolder = os.path.join(patientFolderSourceFull, study, series)
                seriesTargetFolder = os.path.join(patientFolderTargetFull, study, series)
                if not os.path.exists(seriesTargetFolder):
                    os.makedirs(seriesTargetFolder)

                # convert the Dicoms for this series
                for dicomFile in filesBranch:
                    SorceDicomFile = os.path.join(seriesSourceFolder, dicomFile)
                    TargetDicomFile = os.path.join(seriesTargetFolder, dicomFile)
                    parser = DicomParser(SorceDicomFile, recipe= os.path.join(config['VXD_HOME'], 'VxdSort', config['deidRecipe']))
                    parser.define('PatientID_replacement', patientIDs[pctr])
                    parser.define('PatientName_replacement', patientIDs[pctr])
                    parser.parse(strip_sequences=False, remove_private=True)
                    parser.save(TargetDicomFile, overwrite=True)
                print('\t...%s anonymized' % (series))

    return sortedDicomFolderAnon, patientLookup










