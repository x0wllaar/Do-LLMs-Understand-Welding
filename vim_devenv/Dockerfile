FROM docker.io/continuumio/anaconda3

RUN conda install jupyter -y --quiet
RUN pip install json5 openai
RUN pip install torch torchvision torchaudio
RUN pip install transformers
RUN apt-get -y update && \
    apt-get -y install build-essential git autoconf make texinfo gnutls-bin gcc wget curl

RUN pip install flake8 black 'python-lsp-server[all]'

RUN mkdir -p /tmp/neovim && cd /tmp/neovim && \
    wget 'https://github.com/neovim/neovim/releases/download/v0.10.0/nvim-linux64.tar.gz' && \
    tar xzvf nvim-linux64.tar.gz && \
    mkdir -p /opt && mv -v nvim-linux64 /opt && \
    cd / && rm -rf /tmp/neovim
ENV PATH="$PATH:/opt/nvim-linux64/bin"

RUN mkdir -p /root/.config/nvim
COPY init.lua /root/.config/nvim/init.lua
