build:
	sudo apt-get -y update
	sudo apt-get -y install jq
	sudo apt-get -y install cmake
	sudo apt-get -y install unzip
	sudo apt-get -y install wget
	sudo apt-get -y install python3-pip
	sudo apt-get -y install curl
	sudo curl -ssL https://get.docker.com | bash
	sudo curl -L https://github.com/docker/compose/releases/download/1.29.1/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
	sudo chmod +x /usr/local/bin/docker-compose
	export TZ=UTC
	sudo wget https://services.gradle.org/distributions/gradle-6.7.1-bin.zip -P /tmp
	unzip -d /opt/gradle /tmp/gradle-*.zip
	export GRADLE_HOME=/opt/gradle/gradle-6.7.1
	export PATH=${GRADLE_HOME}/bin:${PATH}
	SUB_BUILD=PLATFORM ./gradlew build
