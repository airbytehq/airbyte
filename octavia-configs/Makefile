.PHONY: forward_ec2_port install_octavia

forward_ec2_port:
	cd $(HOME)/.ssh && \
	ssh -i "airbyte.pem" -L 8000:localhost:8000 -N -f ec2-user@ec2-35-178-251-14.eu-west-2.compute.amazonaws.com

install_octavia:
	curl -s -o- https://raw.githubusercontent.com/airbytehq/airbyte/master/octavia-cli/install.sh | bash; \
	echo "AIRBYTE_URL=http://host.docker.internal:8000" >> $(HOME)/.octavia;
