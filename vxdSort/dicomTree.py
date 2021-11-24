# program to examine the contents of sorted folder (after running vxdSort.py), and create a tree structure describing
# the contents of the folder


from vxdTools.splitall import splitall
from vxdTools.readConfigFile import readConfigFile

class dTree:

    def __init__(self, sorter):
        # the sorter object contains a list of all the dicom folders which have been created during vxdSort
        # this is stored in the sorter.renamedFiles dict, in which the keys are the folder names, and the values are
        # the files within each folder

        # examine the config['defaultTargetPattern'] string pattern, to find where PatientName, StudyDate, and SeriesDescription are
        # load the default parameters from the config file
        config = readConfigFile()
        targetParts = config['defaultTargetPattern'].split('/')  # TODO: check compatibility with Windows
        targetPartsNumItems = len(targetParts)
        targetPartsPatientIndex = targetParts.index('%PatientName')
        targetPartsStudyIndex = targetParts.index('%StudyDate')
        targetPartsSeriesIndex = targetParts.index('%SeriesNumber-%SeriesDescription')

        # get a list of all patients within the root folder
        self.patients = []
        for folder in sorter.renamedFiles:
            subFoldersInPath = splitall(folder)

            # these are folder names, so don't include the filename
            # so subtract one from targetPartsNumItems, as last part is filename
            # then count backwards from the end
            patientName = subFoldersInPath[-(targetPartsNumItems-1-targetPartsPatientIndex)]
            if patientName not in self.patients:
                self.patients.append(patientName)

        # create the tree, with one branch per patient
        dtree = {}
        self.patients.sort()
        self.tree = dtree.fromkeys(self.patients)

        # for each patient, list the number of studies
        for patient in self.patients:
            studies = []
            for folder in sorter.renamedFiles:
                subFoldersInPath = splitall(folder)
                patientName = subFoldersInPath[-(targetPartsNumItems-1-targetPartsPatientIndex)]
                if patientName == patient:
                    # assume the subFolder second from the end is the study date
                    studyDate = subFoldersInPath[-(targetPartsNumItems-1-targetPartsStudyIndex)]
                    if studyDate not in studies:
                        studies.append(studyDate)

            studiesDict = {}
            studies.sort()
            studiesDict = studiesDict.fromkeys(studies)
            for study in studies:
                series = []
                for folder in sorter.renamedFiles:
                    subFoldersInPath = splitall(folder)
                    studyDate = subFoldersInPath[-(targetPartsNumItems-1-targetPartsStudyIndex)]
                    if studyDate in study:
                        thisSeries = subFoldersInPath[-(targetPartsNumItems-1-targetPartsSeriesIndex)]
                        if thisSeries not in series:
                            series.append(thisSeries)

                seriesDict = {}
                series.sort()
                seriesDict = seriesDict.fromkeys(series)
                for thisSeries in series:
                    for folder in sorter.renamedFiles:
                        subFoldersInPath = splitall(folder)
                        thisFolderPatientName = subFoldersInPath[-(targetPartsNumItems-1-targetPartsPatientIndex)]
                        thisFolderStudyDate = subFoldersInPath[-(targetPartsNumItems-1-targetPartsStudyIndex)]
                        thisFolderSeries = subFoldersInPath[-(targetPartsNumItems-1-targetPartsSeriesIndex)]
                        if thisFolderPatientName in patient and thisFolderStudyDate in study and thisFolderSeries in thisSeries:
                            # list the files in this directory
                            files = sorter.renamedFiles[folder]
                            files.sort()
                            seriesDict[thisSeries] = files

                studiesDict[study] = seriesDict

            self.tree[patient] = studiesDict


    def printTree(self):
        # loop through the self.tree and print the structure
        for pctr, patient in enumerate(self.tree):
            print('')
            print('-Patient %d: %s' % (pctr+1, patient))
            for studyctr, study in enumerate(self.tree[patient]):
                print('\t-Study %d: %s' % (studyctr+1, study))
                for seriesctr, series in enumerate(self.tree[patient][study]):
                    thisSeries = self.tree[patient][study][series]
                    if series is not None and thisSeries is not None:
                        print('\t\tSeries %d:\t %s (%d Files)' % (seriesctr+1, series, len(thisSeries)))






