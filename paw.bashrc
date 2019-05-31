module unload python


export PAW_HOME="/gpfs/alpine/bif112/proj-shared/transient/nopaw"
export SHPROFILE="/gpfs/alpine/bif112/proj-shared/transient/nopaw/paw.bashrc"
#echo "export SHPROFILE=\$(readlink -f $1)"
export PATH="/gpfs/alpine/bif112/proj-shared/transient/nopaw:$PATH"
export PATH="/gpfs/alpine/bif112/proj-shared/transient/nopaw/lib:$PATH"
export PYTHONPATH="/gpfs/alpine/bif112/proj-shared/transient/nopaw/lib:$PYTHONPATH"
export PATH="/ccs/proj/bif112/mongodb/bin:$PATH"
export PATH="/gpfs/alpine/bif112/proj-shared/transient/nopaw/software/miniconda/bin:$PATH"
