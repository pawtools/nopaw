#!/bin/bash

# Current Environment Strategy:
#     Application & Task Runtime:
#     Root conda from fresh
#     download of PPC64le Miniconda version
#     Python 3

echo "-------------------------------------------------"
echo "------ Installing noPAW Test Platform ------"
echo ""
echo "If you are using Summit or a PowerPC architecture"
echo "you will have to modify this setup to provide some"
echo "mechanism of getting MongoDB compatible with the"
echo "hardware, or tunneling to off-site instance."
echo "Mongo for PowerPC has a restrictive license and"
echo "cannot be downloaded with with a command."
echo ""
sleep 10

# CONFIGURATION:
CWD="$(pwd)"
#TESTS_HOME="$PROJWORK/bif112/tests-summit/$INSTALL_NAME"
TESTS_HOME=$(cwd)
MONGO_VERSION="mongodb-linux-ppc64le-enterprise-rhel71-3.6.11"
CONDA_VERSION="Miniconda3-latest-Linux-ppc64le.sh"
PACKAGES_HOME="$TESTS_HOME/packages"

# CREATE PLATFORM SPACE:
mkdir -p $TESTS_HOME
mkdir -p $PACKAGES_HOME

echo "module unload python" >> $SHPROFILE

#----------------------------------------------------------------------#
# MongoDB
if [ -z "$(command -v mongod)" ]; then
  #wget "https://fastdl.mongodb.org/linux/${MONGO_VERSION}.tgz"
  #mv $MONGO_VERSION mongodb
  #rm ${MONGO_VERSION}.tgz
  tar -zxvf ~/tests-summit/extras/${MONGO_VERSION}.tgz -C ./
  mv $MONGO_VERSION mongodb
  echo "export PATH=\"$SOFTWARE_HOME/mongodb/bin:\$PATH\"" >> $SHPROFILE
fi

#----------------------------------------------------------------------#
# Use CONDA
if [ -z "$(command -v conda)" ]; then
  wget "https://repo.continuum.io/miniconda/$CONDA_VERSION"
  bash "$CONDA_VERSION" -b -p miniconda
  rm "$CONDA_VERSION"
  touch $SHPROFILE
  echo "export CONDA=\"$SOFTWARE_HOME/miniconda\"" >> $SHPROFILE
  echo "export PATH=\"\$CONDA/bin:\$PATH\"" >> $SHPROFILE
  source $SHPROFILE
  conda config --add channels omnia --add channels conda-forge
  conda update --yes --all
  conda install --yes $ADAPTIVEMD_DEPENDENCIES
fi

source $SHPROFILE
#----------------------------------------------------------------------#
# We build OpenMM
# - it fails, but gets the simtk package
# - then we install of binaries compiled on summit from
#   conda fails because it doesn't get the simtk layer
#
# Install command (broken)
# this line will run later, 2 wrongs make a working install!
#conda install --yes -c omnia-dev/label/cuda92 openmm
module load cmake
module load cuda/9.1.85

cd $PACKAGES_HOME
git clone https://github.com/pandegroup/openmm.git
cd openmm
mkdir build
cd build

cmake .. -DCUDA_HOST_COMPILER=/sw/summitdev/gcc/7.1.1-20170802/bin/gcc -DCUDA_SDK_ROOT_DIR=/sw/summit/cuda/9.1.85/samples -DCUDA_TOOLKIT_ROOT_DIR=/sw/summit/cuda/9.1.85/ -DCMAKE_CXX_COMPILER=/sw/summitdev/gcc/7.1.1-20170802/bin/g++ -DCMAKE_C_COMPILER=/sw/summitdev/gcc/7.1.1-20170802/bin/gcc -DCMAKE_INSTALL_PREFIX=$PKG_HOME
#cmake .. -DCUDA_HOST_COMPILER=/sw/summitdev/gcc/7.1.1-20170802/bin/gcc -DCUDA_SDK_ROOT_DIR=/sw/summit/cuda/9.1.85/samples -DCUDA_TOOLKIT_ROOT_DIR=/sw/summit/cuda/9.1.85/ -DCMAKE_CXX_COMPILER=/sw/summitdev/gcc/7.1.1-20170802/bin/g++ -DCMAKE_C_COMPILER=/sw/summitdev/gcc/7.1.1-20170802/bin/gcc -DCMAKE_INSTALL_PREFIX=$OPENMM_PREFIX

make -j20 all
make -j20 install 
make -j20 PythonInstall

# Final successful install of OpenMM here
conda install --yes -c omnia-dev/label/cuda92 openmm

#----------------------------------------------------------------------#
cd $PACKAGES_HOME
git clone https://github.com/markovmodel/adaptivemd
cd adaptivemd
python setup.py $ADAPTIVEMD_INSTALL_MODE

# Now moving files over to tests directory
# - use these to get started
echo "module load cuda/9.2.148" >> $SHPROFILE

#----------------------------------------------------------------------#
cd $PACKAGES_HOME
git clone https://github.com/jrossyra/admdgenerator

cat <<EOT >> $SHPROFILE
export ADMD_ACTIVATE="$SHPROFILE"
export ADMD_DEACTIVATE=""
export ADMD_FILES="$TESTS_HOME/mdsystems"
export ADMD_PROFILE="DEBUG"              
export ADMD_ENV=""
export ADMD_WORKFLOWS="$TESTS_HOME/workflows"
export ADMD_SANDBOX="$MEMBERWORK/bif112/admd"
export ADMD_ADAPTIVEMD="$PACKAGES_HOME/adaptivemd"
export ADMD_GENERATOR="$PACKAGES_HOME/admdgenerator"
export ADMD_RUNTIME="\$ADMD_GENERATOR/runtime"
export PATH="\$ADMD_RUNTIME:\$PATH"
export ADMD_DATA="$TESTS_HOME"
export ADMD_DBURL=""
export ADMD_RTMODE=""
export ADMD_NETDEVICE="ib0"   
EOT

cat <<"EOT" >> $SHPROFILE
# NETDEVICE often changed on login vs compute nodes
# this should be pretty general
export ADMD_HOSTNAME=`ip addr show $ADMD_NETDEVICE | grep -Eo '(addr:)?([0-9]*\.){3}[0-9]*' | head -n1`
# this will give unpredictable result if more than 1 mongod running
DBPORT=`netstat -tnulp 2> /dev/null | grep mongod | tail -n1 | awk -F":" '{print $2}' | awk '{print $1}'`
if [ ! -z "$DBPORT" ]; then
  export ADMD_DBURL="mongodb://$ADMD_HOSTNAME:$DBPORT/"
else
  export ADMD_DBURL="mongodb://$ADMD_HOSTNAME:27017/"
fi
export OMP_NUM_THREADS="12"
export OPENMM_CPU_THREADS="$OMP_NUM_THREADS"
EOT

#----------------------------------------------------------------------#
cd $TESTS_HOME
git clone https://github.com/jrossyra/test-workflows workflows

#----------------------------------------------------------------------#
cd $CWD
mkdir $TESTS_HOME/mdsystems
cp -r ../../mdsystems/openmm/* $TESTS_HOME/mdsystems/

#----------------------------------------------------------------------#
echo ""
echo "-------------------------------------------------"
echo "-------------   Install is Done    --------------"
echo ""
echo "Where the tests live:"
echo " $  echo \$TESTS_HOME"
echo " $TESTS_HOME"
echo ""
echo "To read AdaptiveMD environment profile, use"
echo " $  source $SHPROFILE"
echo ""
echo "and now your Python environment"
echo "has the AdaptiveMD stack installed"
echo ""
echo "Go to tests directory"
echo " $  cd $TESTS_HOME/tests"
echo ""
echo "-------------------------------------------------"
echo "-------------------------------------------------"
