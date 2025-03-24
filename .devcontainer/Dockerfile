FROM docker.io/continuumio/anaconda3

RUN conda install jupyter -y --quiet
RUN pip install json5 openai pydantic
RUN pip install torch torchvision torchaudio
RUN pip install transformers
RUN apt-get -y update && apt-get -y install build-essential 

COPY ./run_jupyter.sh /bin/run_jupyter.sh
RUN chmod a+x /bin/run_jupyter.sh

#COPY requirements.txt /tmp/pythonr1.txt
#RUN pip install -r /tmp/pythonr1.txt

CMD ["/bin/run_jupyter.sh"]
