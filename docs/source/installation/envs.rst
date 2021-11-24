========================================================
Setting the Environment Variables and File Permissions
========================================================

Setting the voxelDesk Environment
----------------------------------
In order to run voxelDesk from the command line, the following lines should be added to your ``bash_profile`` (or equivalent) file:

::

    export VXD_HOME=<path to vxdHome folder>
    export PATH=${VXD_HOME}:${PATH}

where the ``vxdHome`` is the folder into which the VoxelDesk source files have been copied.

Once the ``bash_profile`` (or equivalent) file has been modified, either open a new terminal window to apply the changes, or type:

::

    source ~/.bash_profile

in the existing terminal window.

It is worth checking at this point that the FSL environment variables have also been set up (the FSL installer should have taken care of this).
Check that the folllowing lines, or something similar, are present in your ``bash_profile`` (or equivalent) file:

::

    FSLDIR=/usr/local/fsl
    PATH=${FSLDIR}/bin:${PATH}
    export FSLDIR PATH
    . ${FSLDIR}/etc/fslconf/fsl.sh



Setting File Permissions
----------------------------------

Navigate to the ``VXD_HOME`` folder:

::

    cd $VXD_HOME

The python files in this parent folder are the core voxelDesk command-line functions.
These need to be given execute permission, using the following command:

::

    chmod +x *.py

Once the above steps are complete, the command-line functions can be executed from any location.

Verifying the Installation
-----------------------------
You can verify the installation and setup have been successful by opening a terminal window, and running:

::

    vxdSort.py --help

This should display the guidance for running ``vxdSort`` in the terminal window.

.. note::

    If the above dose not work, make sure the *vxd* conda environment is active (you should see (vxd) at the
    command prompt). If it isn't, type:

    .. code-block:: text

        conda activate vxd

    The vxd conda environment should always be activated before running voxelDesk commands.


