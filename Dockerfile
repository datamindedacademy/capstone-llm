FROM public.ecr.aws/dataminded/v4.0.1-hadoop-3.4.2-v4

USER 0
ENV PYSPARK_PYTHON python3
WORKDIR /opt/spark/work-dir

#TODO add your project code and dependencies to the image
