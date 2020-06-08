FROM continuumio/miniconda3

RUN apt-get -y update && apt-get -y install build-essential gcc

RUN conda install python=3.7 nomkl scipy numpy cython pip pytest

