.PHONY:

SERVER =
USER = ec2-user
DIR := ${CURDIR}
KEY = airbyte_test.pem
TEMP_DIR = temp_dir


get_docker_compose:


forward_ec2_port:
	ssh -i $(HOME)/.ssh/$(KEY) -L 8000:localhost:8000 -N -f $(USER)@$(SERVER);

create_temp_dir:
	ssh -i $(HOME)/.ssh/$(KEY) $(USER)@$(SERVER) 'mkdir ~/$(TEMP_DIR)';

create_data_dir:
	ssh -i $(HOME)/.ssh/$(KEY) $(USER)@$(SERVER) 'sudo mkdir /data';

mount_ebs:
	ssh -i $(HOME)/.ssh/$(KEY) $(USER)@$(SERVER) 'sudo mkfs -t xfs /dev/xvdf';
	ssh -i $(HOME)/.ssh/$(KEY) $(USER)@$(SERVER) 'sudo mount /dev/xvdf /var/lib/docker/';

install_docker:
	ssh -i $(HOME)/.ssh/$(KEY) $(USER)@$(SERVER) 'sudo yum install -y docker'; \
	ssh -i $(HOME)/.ssh/$(KEY) $(USER)@$(SERVER) 'sudo wget https://github.com/docker/compose/releases/download/1.26.2/docker-compose-Linux-x86_64 -O /usr/local/bin/docker-compose'; \
	ssh -i $(HOME)/.ssh/$(KEY) $(USER)@$(SERVER) 'sudo chmod +x /usr/local/bin/docker-compose'; \
	ssh -i $(HOME)/.ssh/$(KEY) $(USER)@$(SERVER) 'sudo usermod -a -G docker $(USER)';

start_docker:
	ssh -i $(HOME)/.ssh/$(KEY) $(USER)@$(SERVER) 'sudo service docker start';

copy_docker_compose_to_ec2:
	scp -i $(HOME)/.ssh/$(KEY) ${DIR}/docker-compose.yaml $(USER)@$(SERVER):~/$(TEMP_DIR)/docker-compose.yaml;

copy_env_file:
	scp -i $(HOME)/.ssh/$(KEY) ${DIR}/.env.prod $(USER)@$(SERVER):~/$(TEMP_DIR)/.env

move_docker_compose_file_to_data_folder:
	ssh -i $(HOME)/.ssh/$(KEY) $(USER)@$(SERVER) 'sudo cp ~/$(TEMP_DIR)/docker-compose.yaml /data/docker-compose.yaml';

move_env_file_to_data_folder:
	ssh -i $(HOME)/.ssh/$(KEY) $(USER)@$(SERVER) 'sudo cp ~/$(TEMP_DIR)/.env /data/.env';

run_docker_compose_up:
	ssh -i $(HOME)/.ssh/$(KEY) $(USER)@$(SERVER) "cd /data ; docker-compose up -d;";
	
check_running_containers:
	ssh -i $(HOME)/.ssh/$(KEY) $(USER)@$(SERVER) 'docker ps';

install_octavia_locally:
	curl -s -o- https://raw.githubusercontent.com/airbytehq/airbyte/master/octavia-cli/install.sh | bash; \
	echo "AIRBYTE_URL=http://host.docker.internal:8000" >> $(HOME)/.octavia;

disaster_recovery: create_data_dir create_temp_dir install_docker mount_ebs copy_docker_compose_to_ec2 copy_env_file move_docker_compose_file_to_data_folder \
	move_env_file_to_data_folder start_docker run_docker_compose_up;

generate_passwords:
	sh ./secrets_generator.sh;

octavia_apply:
	docker run -i --rm -v $(DIR)/octavia-configs:/home/octavia-project \
	--network host \
	--user $(id -u):$(id -g) \
	--env-file $(HOME)/.octavia \
	--env OCTAVIA_ENABLE_TELEMETRY=False \
	--env AIRBYTE_URL=http://host.docker.internal:8000 \
	airbyte/octavia-cli:0.40.28 apply;