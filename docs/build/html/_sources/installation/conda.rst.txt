.. _conda_venv:

=========================================
Creating the Conda Virtual Environment
=========================================

It is recommended that you create a fresh Conda virtual environment, into which the required packages will be installed.
This will create a self-contained environment, and avoid causing conflicts with any existing packages and software.

To do this, first navigate to the following folder:

::

    cd <vxdHome>/vxdSetup

where ``<vxdHome>`` is the name of the parent folder into which voxelDesk was installed.

Next, create the conda virtual environment, using the ``environment.yml`` file:

::

    conda env create -f environment.yml

This will create a new virtual environment named ``vxd``, into which the required python modules will be installed.
In addition, third-party applications such as *mrtrix3*, *dcm2niix*, and *Grassroots DICOM* will be installed within this environment.

The ``vxd`` virtual environment should now be activated, using:

::

    conda activate vxd





