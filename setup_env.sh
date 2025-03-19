#!/bin/bash

export WORKSPACE_PATH=/your/workspace/path


export PATH=/disk03/usr8/schen/software/cmake-3.20.2/bin:$PATH
# Environment for HK fiTQun
source /disk03/usr8/schen/software/root_install_py36/bin/thisroot.sh
source /disk03/usr8/schen/software/geant4-install/bin/geant4.sh
source /disk03/usr8/schen/software/geant4-10.3.3/build/geant4make.sh
export PATH=/disk03/usr8/schen/software/hepmc3-install/bin:$PATH
export LD_LIBRARY_PATH=/disk03/usr8/schen/software/hepmc3-install/lib64:$LD_LIBRARY_PATH

export GEANT4_HOME=/disk03/usr8/schen/software/geant4-install/
export PATH=$GEANT4_HOME/bin:$PATH
export LD_LIBRARY_PATH=$GEANT4_HOME/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/disk03/usr8/schen/software/root_install_py36/lib:$LD_LIBRARY_PATH

# export WCSIM_BUILD_DIR=/disk03/usr8/schen/software/WCSim/WCSim_build/
# export ROOT_INCLUDE_PATH=/disk03/usr8/schen/software/WCSim/WCSim_build/include/WCSim:$ROOT_INCLUDE_PATH
# export PATH=/disk03/usr8/schen/software/WCSim/WCSim_build/bin:$PATH
# export LD_LIBRARY_PATH=/disk03/usr8/schen/software/WCSim/WCSim_build/lib:$LD_LIBRARY_PATH
# export WCSIMDIR=/disk03/usr8/schen/software/WCSim
# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$WCSIMDIR/WCSim_build/src
# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$WCSIMDIR/WCSim_build/include

export WCSIM_BUILD_DIR=/disk03/usr8/schen/software/test_wcsim/WCSim_build/
export ROOT_INCLUDE_PATH=/disk03/usr8/schen/software/test_wcsim/WCSim_build/include/WCSim:$ROOT_INCLUDE_PATH
export PATH=/disk03/usr8/schen/software/test_wcsim/WCSim_build/bin:$PATH                                             
export LD_LIBRARY_PATH=/disk03/usr8/schen/software/test_wcsim/WCSim_build/lib:$LD_LIBRARY_PATH
export WCSIMDIR=/disk03/usr8/schen/software/test_wcsim/WCSim
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$WCSIMDIR/../WCSim_build/src
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$WCSIMDIR/../WCSim_build/include
export WCSIM_SOURCE_DIR=/disk03/usr8/schen/software/test_wcsim/WCSim/


export FITQUN_ROOT=/disk03/usr8/schen/software/fiTQun
