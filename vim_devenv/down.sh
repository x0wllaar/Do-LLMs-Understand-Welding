#!/bin/bash
set -exuo pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
pushd "$SCRIPT_DIR"

source cnt_name.sh

./stop.sh

if "$VIM_CNT_DOCKER_EXECUTABLE" ps -a | sed -r 's/\s+/ /g' | awk 'NR>1' | grep "$CONTAINER_NAME" ; then
	"$VIM_CNT_DOCKER_EXECUTABLE" rm -f "$CONTAINER_NAME"
fi

popd
