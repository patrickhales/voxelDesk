import pydicom
import ntpath
import sys
import numpy as np
from vxdDicom.list_dcm_files import list_dcm_files

class readDicomVolumeEnhanced:
    """
    Notes from https://nipy.org/nibabel/dicom/dicom_orientation.html
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
        ds = pydicom.read_file(dcmFile)

        # For enhanced dicom, the whole volume should be contained in a single dicom file
        # However, we'll keep the class Attributes filled in as per standard dicom

        dcm_files = dcmFile

        # get the parent folder for the reference dicom file
        dcmFolder, dcmFilename = ntpath.split(dcmFile)

        # the set of frames (slices?) are stored in dicom tag (5200, 9230)
        noFrames = int(ds[0x52009230].VM)


        # Now estimate the z location of each slice
        slice_z_locations = []
        ImagePositionPatient_all = np.empty((noFrames, 3))
        ImageOrientationPatient_all = np.empty((noFrames, 6))

        for fctr in range(noFrames):

            thisFrame = ds[0x52009230][fctr]

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

        # check that each file provides a unique slice location, and that gaps between slices are consistent
        if len(z_location_sorted) > 1:
            slice_gaps = np.diff(z_location_sorted)
            mean_slice_gap = np.mean(slice_gaps)
            average_slice_gap_variation = np.mean(abs(slice_gaps-mean_slice_gap))
            max_slice_gap_variation = np.max(abs(slice_gaps-mean_slice_gap))
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

        PixelSpacing = ds[0x52009230][0][0x00289110][0].PixelSpacing
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
        nRows = ds.Rows
        nCols = ds.Columns

        if nSlices == 1:
            img = ds.pixel_array
        else:
            img = np.zeros((nRows, nCols, nSlices))
            # read in the raw pixel_array
            img_raw = ds.pixel_array
            # this will be saved with slices as the first dimenion, for 3D data
            #TODO: check what happens when data is 4D
            if img_raw.shape[0] == nSlices:
                img = img_raw.reshape(img_raw, (int(img_raw.shape[1]), int(img_raw.shape[2]), int(img_raw.shape[0])))


        # define the final class attributes
        self.dcmFolder = dcmFolder
        self.dcmRefFile = dcmFile
        self.dcmFiles = dcmFile
        self.nRows = nRows
        self.nCols = nCols
        self.row_pixel_spacing = float(row_pixel_spacing)
        self.col_pixel_spacing = float(col_pixel_spacing)
        self.nSlices = nSlices
        self.sliceLocations = z_location_sorted
        self.ImagePositionPatient = ImagePositionPatient_sorted
        self.Md = Md
        self.img = img

