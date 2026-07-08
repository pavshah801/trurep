FROM python:3.9-slim
WORKDIR /trulux
COPY ./requirements.txt /trulux
RUN pip3 install -r ./requirements.txt
RUN apt-get update                             \
 && apt-get install -y --no-install-recommends \
    ca-certificates curl firefox-esr           \
 && rm -fr /var/lib/apt/lists/*                \
 && curl -L https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz | tar xz -C /usr/local/bin \
 && apt-get purge -y ca-certificates curl
COPY ./README.md /trulux
COPY ./trulux_app.py /trulux
COPY ./data_trulux /trulux/data_trulux
COPY ./testmodels /trulux/testmodels
COPY ./testmodelsupd /trulux/testmodelsupd
ENV ENV_BRND=Longines
ENV MONGO_STRING=mongodb://mongoservice:27017/Trulux_catalogue
ENTRYPOINT ["python"]
CMD ["trulux_app.py"]