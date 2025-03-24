#!/bin/bash
set -exuo pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
pushd "$SCRIPT_DIR/.."

export REAL_WORKSPACE_PATH="$(pwd)"
export VIM_CNT_DOCKER_EXECUTABLE="docker"
export VIM_CNT_LOCAL_PATH_RESOLVED="$(realpath $SCRIPT_DIR)/vim_config"

if ! test -z "${WSL_DISTRO_NAME+x}" ; then
    export REAL_WORKSPACE_PATH="$(wslpath -m .)"
    export VIM_CNT_LOCAL_PATH_RESOLVED="$(cd $VIM_CNT_LOCAL_PATH_RESOLVED && wslpath -m .)"
    export VIM_CNT_DOCKER_EXECUTABLE="docker.exe"
fi

CONTAINER_NAME_HASH=$(echo "$REAL_WORKSPACE_PATH" | sha512sum | head -c10)
export CONTAINER_NAME="devcnt$CONTAINER_NAME_HASH"

export CNT_IMAGE_NAME="vimdevcnt$CONTAINER_NAME_HASH"

if test -z "${VIM_CNT_GLOBAL_PATH+x}" ; then
   VIM_CNT_GLOBAL_PATH="$HOME/.nvim_global_config/"
   if ! test -z "${WSL_DISTRO_NAME+x}" ; then
       VIM_CNT_GLOBAL_PATH="${WINHOME:-$HOME}/nvim_global_config"
   fi
fi


if ! test -d "$VIM_CNT_GLOBAL_PATH" ; then
   VIM_CNT_GLOBAL_PATH="$(mktemp -d)"
   touch "$VIM_CNT_GLOBAL_PATH/init.lua"
   touch "$VIM_CNT_GLOBAL_PATH/pre_lazy.lua"
   touch "$VIM_CNT_GLOBAL_PATH/plugins.lua"
fi

export VIM_CNT_GLOBAL_PATH_RESOLVED="$VIM_CNT_GLOBAL_PATH"
if ! test -z "${WSL_DISTRO_NAME+x}" ; then
    export VIM_CNT_GLOBAL_PATH_RESOLVED="$(cd $VIM_CNT_GLOBAL_PATH_RESOLVED && wslpath -m .)"
fi

popd
