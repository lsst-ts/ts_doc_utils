***********************
Puppet Version Metadata
***********************

* https://github.com/lsst-it/lsst-itconf - uses puppet-ccs-software, installs ccs this way
* https://github.com/lsst-it/puppet-ccs_software - source of information

Currently the Camera Control System installs multiple versions of the software on the same machines via puppet.
We could use this to generate a list of potential versions that could be installed, but not sure how useful that is.
They use symlinks to distinguish between dev and prod software versions running.
This could be handled by puppet in the future.

The version table is currently generated from a script located on the one of the ccs computers.
It generates two text files, one of which is just TAB delimited version numbers and the other is formatted for `Confluence <https://confluence.lsstcorp.org/display/LSSTCOM/Currently+running+CCS+ComCam+software>`_.
This process is not automated yet.
