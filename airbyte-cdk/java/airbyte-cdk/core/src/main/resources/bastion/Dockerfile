FROM ubuntu:24.04

RUN apt-get update && apt-get install -y openssh-server
RUN apt-get install -y apt-utils
RUN mkdir -p /var/run/sshd
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config

RUN useradd -m -s /bin/bash sshuser
RUN echo "sshuser:secret" | chpasswd
RUN echo "root:secret" | chpasswd

RUN mkdir -p /var/bastion
RUN ssh-keygen -m PEM -t rsa -b 4096 -C "test-container-bastion" -P "" -f /var/bastion/id_rsa -q
RUN install -D /var/bastion/id_rsa.pub /home/sshuser/.ssh/authorized_keys

RUN chown -R sshuser:sshuser /home/sshuser/.ssh
RUN chmod 600 /home/sshuser/.ssh/authorized_keys

RUN mkdir -p /root/.ssh

RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
EXPOSE 22

CMD    ["/usr/sbin/sshd", "-D"]
