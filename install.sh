#!/bin/bash

echo ""
echo "-------------------------------------------------"
echo ""
echo "If you are on a funny architecture and cannot use"
echo "an automatically downloaded MongoDB version, get"
echo "whichever MongoDB you have into your path so that"
echo "a \`which mongod\` command reports the location"
echo "before running this script:"
echo "PATH=/path/to/mongo/bin:\$PATH"
sleep 10
echo ""
echo "-------------------------------------------------"
echo "-------- Installing noPAW Test Platform ---------"
echo ""
echo "You may have to modify this setup to provide some"
echo "mechanism of getting MongoDB compatible with the"
echo "hardware, or tunneling to off-site instance."
echo ""
echo "For example, Mongo for PowerPC has a restrictive license"
echo "and cannot be easily downloaded on the command line."
echo "(see above message about having the installer hook"
echo " on to whatever mongo you do have)"
echo ""
echo "If you have your mongod situatated and are ready to proceed"
echo ""
read -t 1 -n 99999 discard
read -n 1 -p  " >>> then type \"y\": " proceedinput

if [ ! "$proceedinput" = "y" ]
then
  echo "Quitting"
  echo ""
  exit 0
fi

#----------------------------------------------------------------------#
# CONFIGURATION:
# TODO configuration file for a tiny! number of install options
#SOFTWARE_HOME="/ccs/proj/bif112/nopaw/software"
SOFTWARE_HOME="$(pwd)/software"
MONGO_VERSION="mongodb-linux-ppc64le-enterprise-rhel71-3.6.11"
CONDA_VERSION="Miniconda3-latest-Linux-ppc64le.sh"
PYTHON_REQS="pymongo pyyaml numpy=1.15"

#----------------------------------------------------------------------#
#                              INSTALL STARTS                          #
#----------------------------------------------------------------------#
CWD="$(pwd)"
SHPROFILE="$CWD/rt.bashrc"

# CREATE PLATFORM SPACE:
mkdir -p "$CWD/sessions"
mkdir -p "$SOFTWARE_HOME"

echo "module unload python" >> $SHPROFILE
echo "" >> $SHPROFILE
echo "export PAW_HOME=\"$CWD\"" >> $SHPROFILE
echo "export SHPROFILE=\"$SHPROFILE\"" >> $SHPROFILE
echo "export PATH=\"$CWD:\$PATH\"" >> $SHPROFILE
echo "export PATH=\"$CWD/lib:\$PATH\"" >> $SHPROFILE
echo "export PYTHONPATH=\"$CWD/lib/anylz:\$PYTHONPATH\"" >> $SHPROFILE

#----------------------------------------------------------------------#
# Install MongoDB
if [ -z "$(command -v mongod)" ]
then
  cd $SOFTWARE_HOME
  if [ ! -d "mongodb" ]
  then
    wget "https://fastdl.mongodb.org/linux/${MONGO_VERSION}.tgz"
    mv $MONGO_VERSION mongodb
    rm ${MONGO_VERSION}.tgz
    echo "export PATH=\"$SOFTWARE_HOME/mongodb/bin:\$PATH\"" >> $SHPROFILE
  else
    echo "Found 'mongodb' folder in the given software directory"
    echo "  --> aborting mongodb install"
    sleep 5
  fi
  cd $CWD
elif [ ! -z "$(which mongod)" ]
then
  echo "export PATH=\"$(dirname $(which mongod)):\$PATH\"" >> $SHPROFILE
else
  echo "Your platform will probably not work, no known"
  echo "mongodb component is available"
fi

#----------------------------------------------------------------------#
# Install Conda
if [ -z "$(command -v conda)" ]
then
  cd $SOFTWARE_HOME
  if [ ! -d "miniconda" ]
  then
    wget "https://repo.continuum.io/miniconda/$CONDA_VERSION"
    bash "$CONDA_VERSION" -b -p miniconda
    rm "$CONDA_VERSION"
    echo "export PATH=\"$SOFTWARE_HOME/miniconda/bin:\$PATH\"" >> $SHPROFILE
    source $SHPROFILE
    conda config --add channels omnia --add channels conda-forge
    conda update --yes --all
    conda install --yes $PYTHON_REQS
  else
    echo "Found 'miniconda' folder in the given software directory"
    echo "  --> aborting conda install"
    sleep 5
  fi
  cd $CWD
fi

#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
echo ""
echo "-------------------------------------------------"
echo "-------------   Install is Done    --------------"
echo ""
echo "To use nopaw tests, source this environment profile"
echo " $ source $SHPROFILE"
echo ""
echo "-------------------------------------------------"
echo "-------------------------------------------------"

