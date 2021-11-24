# function to adapt an existing dicom UID, preserving the prefix which contains useful info re. the hospital / scanner etc

import pydicom

def adapt_dicom_uid(uid):

    # keep the first parts, as these contain useful info about the hospital / scanner etc
    uid_parts = uid.split('.')
    # the sub-section which is longest will be the bit we change
    uid_long_part = max(uid_parts, key=len)
    uid_prefix = uid[0:uid.index(uid_long_part)]
    # create a new UID
    uid_new = pydicom.uid.generate_uid(prefix=uid_prefix)

    return uid_new
