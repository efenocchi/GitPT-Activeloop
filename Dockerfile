# read the doc: https://huggingface.co/docs/hub/spaces-sdks-docker
# you will also find guides on how best to write your Dockerfile

FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt



RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY --chown=user . $HOME/app

RUN mkdir -p $HOME/app/data

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]