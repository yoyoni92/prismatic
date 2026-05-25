FROM n8nio/runners:latest

USER root

COPY requirements.txt /opt/runners/task-runner-python/requirements.txt
RUN cd /opt/runners/task-runner-python && uv pip install -r requirements.txt

USER runner
