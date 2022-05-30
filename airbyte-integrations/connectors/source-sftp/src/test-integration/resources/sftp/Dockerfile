FROM ubuntu:18.04

RUN apt-get update && apt-get install -y openssh-server
RUN apt-get install -y apt-utils
RUN mkdir /var/run/sshd
RUN sed -i 's/PasswordAuthentication yes/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config

RUN useradd -m -s /bin/bash sftpuser
RUN echo "sftpuser:pass" | chpasswd

RUN mkdir /var/sftp
RUN ssh-keygen -m PEM -t rsa -b 4096 -C "test-container-sftp" -P "" -f /var/sftp/id_rsa -q
RUN install -D /var/sftp/id_rsa.pub /home/sftpuser/.ssh/authorized_keys

RUN chown -R sftpuser:sftpuser /home/sftpuser/.ssh
RUN chmod 600 /home/sftpuser/.ssh/authorized_keys

RUN mkdir /root/.ssh

RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
EXPOSE 22

CMD    ["/usr/sbin/sshd", "-D"]