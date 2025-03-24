#!/bin/bash
set -exuo pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
pushd "$SCRIPT_DIR"

source cnt_name.sh

./build.sh

if ! "$VIM_CNT_DOCKER_EXECUTABLE" ps -a | sed -r 's/\s+/ /g' | awk 'NR>1' | grep "$CONTAINER_NAME" ; then
	"$VIM_CNT_DOCKER_EXECUTABLE" create --name "$CONTAINER_NAME" \
        -v "$REAL_WORKSPACE_PATH:/code:rw" \
        -v "$VIM_CNT_LOCAL_PATH_RESOLVED:/root/.config/nvim/lua/local:rw" \
        -v "$VIM_CNT_GLOBAL_PATH_RESOLVED:/root/.config/nvim/lua/global:rw" \
        "$CNT_IMAGE_NAME" sleep infinity
fi

if ! "$VIM_CNT_DOCKER_EXECUTABLE" ps | sed -r 's/\s+/ /g' | awk 'NR>1' | grep "$CONTAINER_NAME" ; then
        "$VIM_CNT_DOCKER_EXECUTABLE" start "$CONTAINER_NAME"
fi

"$VIM_CNT_DOCKER_EXECUTABLE" exec -it --detach-keys="ctrl-@" \
-e LC_ALL="C.UTF-8" -e LANG="C.UTF-8" \
-w "/code" \
"$CONTAINER_NAME" /bin/bash

popd
