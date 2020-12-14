FROM python:3.8

ARG PROJECT=ProxyPool
RUN mkdir /opt/$PROJECT/
WORKDIR /opt/$PROJECT
ADD ./requirements.txt /opt/$PROJECT/requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt -i http://pypi.douban.com/simple --trusted-host pypi.douban.com

WORKDIR /usr/bin
RUN ln -s pip3 pip
WORKDIR /opt/$PROJECT
COPY ./ /opt/$PROJECT/
