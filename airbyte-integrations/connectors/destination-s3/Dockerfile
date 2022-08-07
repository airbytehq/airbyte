FROM airbyte/integration-base-java:dev AS build

WORKDIR /airbyte

ENV APPLICATION destination-s3

COPY build/distributions/${APPLICATION}*.tar ${APPLICATION}.tar

RUN tar xf ${APPLICATION}.tar --strip-components=1 && rm -rf ${APPLICATION}.tar

FROM airbyte/integration-base-java:dev

WORKDIR /airbyte

ENV APPLICATION destination-s3

COPY --from=build /airbyte /airbyte
RUN apt-get update
RUN apt-get install lzop liblzo2-2 liblzo2-dev wget curl unzip zip build-essential maven git -y
RUN wget http://www.oberhumer.com/opensource/lzo/download/lzo-2.10.tar.gz -P /tmp
RUN cd /tmp && tar xvfz lzo-2.10.tar.gz
RUN cd /tmp/lzo-2.10/ && ./configure --enable-shared --prefix /usr/local/lzo-2.10
RUN cd /tmp/lzo-2.10/ && make
RUN cd /tmp/lzo-2.10/ && make install
RUN git clone https://github.com/twitter/hadoop-lzo.git /usr/lib/hadoop/lib/hadoop-lzo/
RUN curl -s "https://get.sdkman.io" | bash
RUN /bin/bash -c "source /root/.sdkman/bin/sdkman-init.sh; sdk version; sdk install java 8.0.342-librca; sdk use java 8.0.342-librca; java- version; cd /usr/lib/hadoop/lib/hadoop-lzo/ && C_INCLUDE_PATH=/usr/local/lzo-2.10/include LIBRARY_PATH=/usr/local/lzo-2.10/lib mvn clean test; mvn package"
RUN /bin/bash -c "find /usr/lib/hadoop/lib/hadoop-lzo/ -name '*libgplcompression*' -exec cp {} /usr/lib/  \;"
RUN export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib/hadoop/lib/native/
RUN java -version
LABEL io.airbyte.version=0.3.12
LABEL io.airbyte.name=airbyte/destination-s3
