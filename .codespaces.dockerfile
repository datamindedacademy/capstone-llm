FROM mcr.microsoft.com/vscode/devcontainers/python:3.13-bookworm 

USER root

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install Java 17 and ACL
RUN apt-get update && apt-get install -y openjdk-17-jdk acl

# Install Conveyor
RUN wget https://app.conveyordata.com/api/info/cli/location/linux/amd64 -O conveyor_linux_amd64.tar.gz && \
    tar -zxvf conveyor_linux_amd64.tar.gz && \
    chmod +x bin/linux/amd64/conveyor &&\
    cp bin/linux/amd64/conveyor /usr/local/bin/conveyor

# Install AWS CLI
RUN wget "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -O "awscliv2.zip" && \
    unzip awscliv2.zip && \
    rm -rf awscliv2.zip && \
    sudo ./aws/install --install-dir /opt/aws-cli --bin-dir /usr/local/bin/ && \
    sudo chmod a+x /opt/

USER vscode