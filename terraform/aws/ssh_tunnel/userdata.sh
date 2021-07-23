#!/bin/bash -e

# Apply security patches
sudo yum update -y

# Create a non-root user for use by the airbyte connectors.
sudo adduser airbyte -m
sudo su - airbyte bash -c "mkdir ~/.ssh && chmod 700 ~/.ssh && touch ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
sudo su - airbyte bash -c "cat > /home/airbyte/.ssh/authorized_keys <<EOF 
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDISW6oFBHzGT+Y+BDc5NSg8PcPfdbHnX71pdfVufB++Do5HdvPLY1Jyb47mv0aTxg+Au/akh8OcDV0JVuis6QfMzmbA92dwhhSrUNj3OPWl7YDcywSzwWz3qL8PL1sjaLiIKcFYfNhuJWEZP8ubCkQulsNcqZm8G+/0R8bkbURaQy8Dp78DWYh6hf/40ln07UW1VlM2ja6t0nCJDDBLNCpWD3L7XvlF5UmpwGKX1Dp8d7AtwDSn1qnRDJgpfNHLGu5Ag1a4ohP+HQL3Syu/dmh06oNKJ9Jr6s057nhXC3FKj4TNZ2YwY16cepzw4xVopNkeE5gAPmS47OVEh03XFE0h9uu/lg6/atxKjVF5ppe+kvwlvucJTBosn3uOgjSl3cwNd6Kwe3LAGdEZYCs/BLtXoFAkkY2GuHSN7Xrai+lVPZtFICRGMGA236nrnZs4u38LX7rhf5jspHrCdkkskTAEcQ2v8J6h4YCbr7BTltIG+8XsyHGuYUESYHfe2N0Tqc= airbyte
EOF"

# TODO: Figure out if connectors should use password auth or ssh keys for this, or support both.

