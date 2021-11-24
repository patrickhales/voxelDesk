================================
Installation Instructions
================================

Dependencies
-------------
VoxelDesk is a library of python tools. It requires python 3.x, and it is recommended to use version 3.8 or higher.

.. note::

    **Windows Users**

    Some voxelDesk functions utilize third-party applications which require a unix-style environment (such as `FSL <https://fsl.fmrib.ox.ac.uk/fsl/fslwiki>`_).

    As such, it is recommended to first install the Windows Subsystem for Linux (WSL - requires Windows 10). Installation instructions for WSL can be found `here <https://docs.microsoft.com/en-us/windows/wsl/install>`_

    After installing WSL, the following instructions can be followed from within the WSL shell.

Anaconda
*********
Most python modules and non-python binaries which voxelDesk depends on can be easily installed in a single step,
using Anaconda (see :ref:`conda_venv`). As such, if not already installed, it is recommended to first install `Anaconda <https://www.anaconda.com/>`_.

FSL
*********
In addition, some voxelDesk functions utilize the Oxford FMRIB Software Library *FSL*. Instructions for installing
and setting up FSL can be found `here <https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation>`_.






