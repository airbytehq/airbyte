FROM linuxkit/sshd:v1.0.0

# enable logging in as `sshuser` with password `secret`
RUN sed -i 's/#PermitRootLogin yes/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -ri 's/PasswordAuthentication no/PasswordAuthentication yes/g' /etc/ssh/sshd_config
RUN adduser -D -g "sshuser" sshuser -G wheel
RUN echo -e "secret\nsecret" | passwd sshuser

# enable logging in as `sshuser` a key exposed in `/var/bastion/id_rsa`
RUN mkdir /var/bastion
RUN ssh-keygen -m PEM -t rsa -b 4096 -C "test-container-bastion" -P "" -f /var/bastion/id_rsa -q
RUN install -D /var/bastion/id_rsa.pub /home/sshuser/.ssh/authorized_keys
RUN chown -R sshuser:wheel /home/sshuser/.ssh
RUN chmod 600 /home/sshuser/.ssh/authorized_keys
