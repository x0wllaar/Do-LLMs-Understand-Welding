#!/bin/sh
jupyter notebook \
    --notebook-dir='/notebooks' \
    --ip='*' --port=8888 \
    --NotebookApp.token="$NOTEBOOK_PASSWORD" \
    --no-browser --allow-root