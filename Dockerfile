FROM public.ecr.aws/dataminded/spark-k8s-glue:v4.0.1-hadoop-3.4.2-v4
USER 0
ENV PYSPARK_PYTHON python3
WORKDIR /opt/spark/work-dir

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .
RUN pip3 install .
