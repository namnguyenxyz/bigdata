FROM bde2020/spark-master:3.1.1-hadoop3.2

ENV SPARK_HOME=/spark

WORKDIR /workspace
COPY requirements.txt /workspace/requirements.txt
RUN pip3 install --no-cache-dir -r /workspace/requirements.txt || true

CMD ["/bin/bash"]
