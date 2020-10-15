#!/usr/bin/env sh

# hack: attempt to get local mounts to work properly
# constraints: ROOT_PARENT better exist on the local filesystem.
# check that the given directory (ROOT) that we plan to use as a mount
# in other containers is a in fact a directory within the parent. if it
# is, then we make sure it is created. we do this by removing the common
# part of the path from the root and appending it to the mount. then we
# make the directories.
# e.g. ROOT_PARENT=/tmp, ROOT=/tmp/airbyte_local MOUNT=/local_parent.
# We create MOUNT_ROOT which will look like /local_parent/airbyte_local.
# Because it is using the mount name, we can create it on the local
# fileystem from within the container.
MOUNT=$1
ROOT_PARENT=$2
ROOT=$3
echo mount
echo $MOUNT
echo root parent
echo ${ROOT_PARENT};
echo root
echo ${ROOT};
[[ "${ROOT}"="${ROOT_PARENT}"* ]] || echo \"ROOT ${ROOT} is not a child of ROOT_PARENT ${ROOT_PARENT}.\"
MOUNT_ROOT=${MOUNT}/$(echo $ROOT | sed -e "s|${ROOT_PARENT}||g");
echo mount root
echo ${MOUNT_ROOT};
mkdir -p ${MOUNT_ROOT};
