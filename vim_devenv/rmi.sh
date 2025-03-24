#!/bin/bash
set -exuo pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
pushd "$SCRIPT_DIR"

source cnt_name.sh

if "$VIM_CNT_DOCKER_EXECUTABLE" image ls -a | grep "$CNT_IMAGE_NAME" ; then
	"$VIM_CNT_DOCKER_EXECUTABLE" image rm -f "$CNT_IMAGE_NAME"
fi

popd
