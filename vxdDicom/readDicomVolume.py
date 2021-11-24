import pydicom
import ntpath
import sys
import numpy as np
from vxdDicom.list_dcm_files import list_dcm_files

class readDicomVolume:
    """
    Notes from https://nipy.org/nibabel/dicom/dicom_orientation.html

    DICOM co-ordinate system
    The x-axis is increasing to the left hand side of the patient (R -> L).
    The y-axis is increasing to the posterior side of the patient (A -> P).
    The z-axis is increasing toward the head of the patient (I -> S).
    ‘Doctor-based coordinate system’ is a better name. Think of a doctor looking at the patient from the foot of the scanner bed.
    Imagine the doctor’s right hand held in front of her like Spiderman about to shoot a web, with her palm towards the patient,
    defining a right-handed coordinate system. Her thumb points to her right (the patient’s left), her index finger points down,
    and the middle finger points at the patient.

    Direction Cosines
    The direction cosines of a vector are the cosines of the angles between the vector and the three coordinate axes.
    If α, β and v are the direction cosines and the Cartesian coordinates of the unit vector v/|v|, and a, b and c are the direction angles of the vector v:
    α = cos(a) = component of v on x
    β = cos(b) = component of v on y
    γ = cos(c) = compenent of v on z
    Remember, cos(0) = 1 and cos(90) = 0, cos(180) = -1, so a direction cosine of 1.0 means v is parallel to that axis.


    Image Orientation (0020,0037) specifies the direction cosines of the first row and the first column with respect to
    the patient. These Attributes shall be provide as a pair. Row value for the x, y, and z axes respectively followed by
    the Column value for the x, y, and z axes respectively.
    The ‘positive row axis’ is left to right, and is the direction of the rows, given by the direction of last pixel in the
    first row from the first pixel in that row. Similarly the ‘positive column axis’ is top to bottom and is the direction
    of the columns, given by the direction of the last pixel in the first column from the first pixel in that column.

    Let’s rephrase: the first three values of ‘Image Orientation Patient’ are the direction cosine for the ‘positive row axis’.
    That is, they express the direction change in (x, y, z), in the DICOM patient coordinate system (DPCS), as you move
    along the row. That is, as you move from one column to the next. That is, as the column array index changes.
    Similarly, the second triplet of values of ‘Image Orientation Patient’ (img_ornt_pat[3:] in Python),
    are the direction cosine for the ‘positive column axis’, and express the direction you move, in the DPCS, as you move
    from row to row, and therefore as the row index changes.

    In dicom,
    i : Column index to the image plane. The first column is index zero.
    j : Row index to the image plane. The first row index is zero.
    In Python, if we have the DICOM pixel data, and we call that pixel_array, then voxel (i, j) in the notation above is
    given by pixel_array[j, i].

    To avoid confusion, we define a flipped version of ‘ImageOrientationPatient’, F, that has flipped columns.
    Now the first column of F contains what the DICOM docs call the ‘column (Y) direction cosine’, and second column
    contains the ‘row (X) direction cosine’. We prefer to think of these as (respectively) the row index direction cosine
    and the column index direction cosine.
    """


    def __init__(self, dcmFile=None):

        # load the reference dicom file
        self.ds = pydicom.read_file(dcmFile)
        self.dcmRefFile = dcmFile

        # get the parent folder for the reference dicom file
        self.dcmFolder, dcmFilename = ntpath.split(dcmFile)

        # Determine if we have standard or enhanced dicom
        enhanced_dicom_flag = False
        if 0x52009230 in self.ds:
            enhanced_dicom_flag = True

        if not enhanced_dicom_flag:
            self.readVolumeStd()
        else:
            self.readVolumeEnhanced()


    def readVolumeStd(self):

        # list all the dicom files in this parent folder
        dcm, dcm_summary = list_dcm_files(self.dcmFolder)

        # dcm is a dictionary with the unique study UIDs as the primary key, the unique series UIDs as the secondary,
        # and the dicom files as the values

        # check the study UID of given dicom file has matches in the parent folder
        if self.ds.StudyInstanceUID not in dcm:
            print('Error: could not find any files with matching Study Instance UID in parent folder')
            sys.exit(1)

        dcm_files = dcm[self.ds.StudyInstanceUID][self.ds.SeriesInstanceUID]

        # Identify all DICOM files in the parent folder which belong to the same volume as the reference file
        # following https://nipy.org/nibabel/dicom/spm_dicom.html
        dcm_volume_files = []
        dcm_excluded_files = []
        for fctr, thisFile in enumerate(dcm_files):
            ds_thisFile = pydicom.read_file(thisFile)
            # following the SPM checklist for matching volumes
            pass_count = 0
            fail_count = 0
            if 'SeriesNumber' in self.ds and 'SeriesNumber' in ds_thisFile:
                if self.ds.SeriesNumber == ds_thisFile.SeriesNumber:
                    pass_count += 1
                else:
                    fail_count += 1
            if 'Rows' in self.ds and 'Rows' in ds_thisFile:
                if self.ds.Rows == ds_thisFile.Rows:
                    pass_count += 1
                else:
                    fail_count += 1
            if 'Columns' in self.ds and 'Columns' in ds_thisFile:
                if self.ds.Columns == ds_thisFile.Columns:
                    pass_count += 1
                else:
                    fail_count += 1
            if 'ImageOrientationPatient' in self.ds and 'ImageOrientationPatient' in ds_thisFile:
                # Note - SPM uses to tolerance of sum squared difference 1e-4
                if self.ds.ImageOrientationPatient == ds_thisFile.ImageOrientationPatient:
                    pass_count += 1
                else:
                    fail_count += 1
            if 'PixelSpacing' in self.ds and 'PixelSpacing' in ds_thisFile:
                # Note - SPM uses to tolerance of sum squared difference 1e-4
                if self.ds.PixelSpacing == ds_thisFile.PixelSpacing:
                    pass_count += 1
                else:
                    fail_count += 1
            # SPM has some additional checks...
            if pass_count == 5:
                dcm_volume_files.append(thisFile)
            else:
                dcm_excluded_files.append(thisFile)

        # We now have a list of files which should come from the same volume as the reference file
        # Now estimate the z location of each slice
        slice_z_locations = []
        ImagePositionPatient_all = np.empty((len(dcm_volume_files), 3))
        ImageOrientationPatient_all = np.empty((len(dcm_volume_files), 6))
        for fctr, thisFile in enumerate(dcm_volume_files):
            ds_thisFile = pydicom.read_file(thisFile)
            x_direction_cosines = np.array((ds_thisFile.ImageOrientationPatient[:3]))  # unit vector pointing along rows (across columns - i.e. column indicies)
            y_direction_cosines = np.array((ds_thisFile.ImageOrientationPatient[3:]))  # unit vector pointing down columns (across rows - i.e. row indicies)
            z_direction_cosines = np.cross(x_direction_cosines, y_direction_cosines)

            # get the z coordinate by taking the dot product of the ‘ImagePositionPatient’ vector and z_dir_cos
            z_location = np.dot(ds_thisFile.ImagePositionPatient, z_direction_cosines)
            slice_z_locations.append(z_location)
            ImagePositionPatient_all[fctr, :] = ds_thisFile.ImagePositionPatient

        # sort the lists by slice_z_location
        dcm_volume_files_sorted = [x for _, x in sorted(zip(slice_z_locations, dcm_volume_files))]
        z_location_sorted = [x for _, x in sorted(zip(slice_z_locations, slice_z_locations))]
        ImagePositionPatient_sorted = [x for _, x in sorted(zip(slice_z_locations, ImagePositionPatient_all))]
        ImageOrientationPatient_sorted = [x for _, x in sorted(zip(slice_z_locations, ImageOrientationPatient_all))]

        # check that each file provides a unique slice location, and that gaps between slices are consistent
        if len(z_location_sorted) > 1:
            slice_gaps = np.diff(z_location_sorted)
            mean_slice_gap = np.mean(slice_gaps)
            average_slice_gap_variation = np.mean(abs(slice_gaps - mean_slice_gap))
            max_slice_gap_variation = np.max(abs(slice_gaps - mean_slice_gap))
            #if average_slice_gap_variation > 1e-4 or max_slice_gap_variation > 1e-4:
            if average_slice_gap_variation > 1e-3 or max_slice_gap_variation > 1e-3:
                print('Error: Slice gap variation (%f) exceeds acceptable limits' % max_slice_gap_variation)
                sys.exit(1)
            if 0 in z_location_sorted:
                print('Error: Slice gap of 0 exists between separate files')
                sys.exit(1)

        """
        Create the general dicom [i,j,k (indicies)] -> [x,y,z (mm)] maxtrix for an arbitary slice within the volume
        T1 is the 3 element vector of the ‘ImagePositionPatient’ field of the first header in the list of headers for this volume.
        TN is the ‘ImagePositionPatient’ vector for the last header in the list for this volume
        """
        # First define the F matrix using the reference dicom file
        x_direction_cosines = np.array((self.ds.ImageOrientationPatient[:3]))  # unit vector pointing along rows (across columns - i.e. column indicies)
        y_direction_cosines = np.array((self.ds.ImageOrientationPatient[3:]))  # unit vector pointing down columns (across rows - i.e. row indicies)
        F = np.hstack((y_direction_cosines.reshape(3, 1), x_direction_cosines.reshape(3, 1)))

        row_pixel_spacing = self.ds.PixelSpacing[0]
        col_pixel_spacing = self.ds.PixelSpacing[1]

        # Now define the slice direction unit vector, using the first and last slice in the volume
        # TODO: adapt for 3D
        T1 = ImagePositionPatient_sorted[0]
        TN = ImagePositionPatient_sorted[-1]
        N = len(z_location_sorted)
        k1 = (TN[0] - T1[0]) / (N - 1)
        k2 = (TN[1] - T1[1]) / (N - 1)
        k3 = (TN[2] - T1[2]) / (N - 1)

        # build the DICOM affine matrix
        col1 = np.append(F[:, 0] * row_pixel_spacing, 0)
        col2 = np.append(F[:, 1] * col_pixel_spacing, 0)
        col3 = np.array([k1, k2, k3, 0])
        col4 = np.array([T1[0], T1[1], T1[2], 1])

        Md = np.hstack((col1.reshape(4, 1), col2.reshape(4, 1), col3.reshape(4, 1), col4.reshape(4, 1)))

        # also read the 3D imaging data
        nSlices = len(dcm_volume_files_sorted)
        nRows = self.ds.Rows
        nCols = self.ds.Columns

        if nSlices == 1:
            img = np.zeros((nRows, nCols))
        else:
            img = np.zeros((nRows, nCols, nSlices))

        for fctr, thisFile in enumerate(dcm_volume_files_sorted):
            ds_thisFile = pydicom.read_file(thisFile)
            if nSlices == 1:
                img = ds_thisFile.pixel_array
            else:
                img[:, :, fctr] = ds_thisFile.pixel_array

        # define the final class attributes
        self.dcmFiles = dcm_volume_files_sorted
        self.nRows = nRows
        self.nCols = nCols
        self.row_pixel_spacing = float(row_pixel_spacing)
        self.col_pixel_spacing = float(col_pixel_spacing)
        self.nSlices = nSlices
        self.sliceLocations = z_location_sorted
        self.ImagePositionPatient = ImagePositionPatient_sorted
        self.Md = Md
        self.img = img
        self.F = F
        self.ImageOrientationPatient = ImageOrientationPatient_sorted


    def readVolumeEnhanced(self):

        # the set of frames (slices?) are stored in dicom tag (5200, 9230)
        noFrames = int(self.ds[0x52009230].VM)

        # Now estimate the z location of each slice
        slice_z_locations = []
        ImagePositionPatient_all = np.empty((noFrames, 3))
        ImageOrientationPatient_all = np.empty((noFrames, 6))

        for fctr in range(noFrames):
            thisFrame = self.ds[0x52009230][fctr]

            ImageOrientationPatient = thisFrame[0x00209116][0].ImageOrientationPatient
            ImagePositionPatient = thisFrame[0x00209113][0].ImagePositionPatient

            x_direction_cosines = np.array(ImageOrientationPatient[:3])  # unit vector pointing along rows (across columns - i.e. column indicies)
            y_direction_cosines = np.array(ImageOrientationPatient[3:])  # unit vector pointing down columns (across rows - i.e. row indicies)
            z_direction_cosines = np.cross(x_direction_cosines, y_direction_cosines)

            # get the z coordinate by taking the dot product of the ‘ImagePositionPatient’ vector and z_dir_cos
            z_location = np.dot(ImagePositionPatient, z_direction_cosines)
            slice_z_locations.append(z_location)
            ImagePositionPatient_all[fctr, :] = ImagePositionPatient
            ImageOrientationPatient_all[fctr, :] = ImageOrientationPatient

        # sort the lists by slice_z_location
        frames_numbers_sorted = [x for _, x in sorted(zip(slice_z_locations, range(noFrames)))]
        z_location_sorted = [x for _, x in sorted(zip(slice_z_locations, slice_z_locations))]
        ImagePositionPatient_sorted = [x for _, x in sorted(zip(slice_z_locations, ImagePositionPatient_all))]
        ImageOrientationPatient_sorted = [x for _, x in sorted(zip(slice_z_locations, ImageOrientationPatient_all))]

        # check that each file provides a unique slice location, and that gaps between slices are consistent
        if len(z_location_sorted) > 1:
            slice_gaps = np.diff(z_location_sorted)
            mean_slice_gap = np.mean(slice_gaps)
            average_slice_gap_variation = np.mean(abs(slice_gaps - mean_slice_gap))
            max_slice_gap_variation = np.max(abs(slice_gaps - mean_slice_gap))
            if average_slice_gap_variation > 1e-4 or max_slice_gap_variation > 1e-4:
                print('Error: Slice gap variation (%f) exceeds acceptable limits' % max_slice_gap_variation)
                sys.exit(1)
            if 0 in z_location_sorted:
                print('Error: Slice gap of 0 exists between separate files')
                sys.exit(1)

        """
        Create the general dicom [i,j,k (indicies)] -> [x,y,z (mm)] maxtrix for an arbitary slice within the volume
        T1 is the 3 element vector of the ‘ImagePositionPatient’ field of the first header in the list of headers for this volume.
        TN is the ‘ImagePositionPatient’ vector for the last header in the list for this volume
        """
        # First define the F matrix using the reference dicom file
        x_direction_cosines = np.array((ImageOrientationPatient_all[0, :3]))  # unit vector pointing along rows (across columns - i.e. column indicies)
        y_direction_cosines = np.array((ImageOrientationPatient_all[0, 3:]))  # unit vector pointing down columns (across rows - i.e. row indicies)
        F = np.hstack((y_direction_cosines.reshape(3, 1), x_direction_cosines.reshape(3, 1)))

        PixelSpacing = self.ds[0x52009230][0][0x00289110][0].PixelSpacing
        row_pixel_spacing = PixelSpacing[0]
        col_pixel_spacing = PixelSpacing[1]

        # Now define the slice direction unit vector, using the first and last slice in the volume
        # TODO: adapt for 3D
        T1 = ImagePositionPatient_sorted[0]
        TN = ImagePositionPatient_sorted[-1]
        N = len(z_location_sorted)
        k1 = (TN[0] - T1[0]) / (N - 1)
        k2 = (TN[1] - T1[1]) / (N - 1)
        k3 = (TN[2] - T1[2]) / (N - 1)

        # build the DICOM affine matrix
        col1 = np.append(F[:, 0] * row_pixel_spacing, 0)
        col2 = np.append(F[:, 1] * col_pixel_spacing, 0)
        col3 = np.array([k1, k2, k3, 0])
        col4 = np.array([T1[0], T1[1], T1[2], 1])

        Md = np.hstack((col1.reshape(4, 1), col2.reshape(4, 1), col3.reshape(4, 1), col4.reshape(4, 1)))

        # also read the 3D imaging data
        nSlices = len(z_location_sorted)
        nRows = self.ds.Rows
        nCols = self.ds.Columns

        if nSlices == 1:
            img = self.ds.pixel_array
        else:
            img = np.zeros((nRows, nCols, nSlices))
            # read in the raw pixel_array
            img_raw = self.ds.pixel_array
            # this will be saved with slices as the first dimension, for 3D data
            # TODO: check what happens when data is 4D
            if img_raw.shape[0] == nSlices:
                img = np.moveaxis(img_raw, 0, -1)

        # define the final class attributes
        self.dcmFiles = self.dcmRefFile
        self.nRows = nRows
        self.nCols = nCols
        self.row_pixel_spacing = float(row_pixel_spacing)
        self.col_pixel_spacing = float(col_pixel_spacing)
        self.nSlices = nSlices
        self.sliceLocations = z_location_sorted
        self.ImagePositionPatient = ImagePositionPatient_sorted
        self.Md = Md
        self.img = img
        self.F = F
        self.ImageOrientationPatient = ImageOrientationPatient_sorted





