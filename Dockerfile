ARG PYTHON_TAG=3.11-alpine
FROM docker.io/python:3.11-alpine
COPY . /app
WORKDIR /app
RUN rm -f /app/.env && python3 -m venv /venv
RUN python3 -m venv /venv
ENV PIPENV_VERBOSITY=-1
ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip3 install pip --upgrade && pip3 install pipenv && pipenv sync
CMD gunicorn -w $(($(nproc)*2+1)) uber_project.wsgi
