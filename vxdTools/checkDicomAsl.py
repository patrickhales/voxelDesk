import pydicom

def checkDicomAsl(dcmFile):
    """ function to check if the passed dicom file is likely to be from an ASL scan"""
    ds = pydicom.dcmread(dcmFile)
    test1 = False
    test2 = False
    if 'ImageType' in ds:
        test1 = any('asl' in i.lower() for i in ds.ImageType)
    if 'ProtocolName' in ds:
        test2 = 'asl' in ds.ProtocolName.lower()
    if test1 or test2:
        asl = True
    else:
        asl = False
    return asl