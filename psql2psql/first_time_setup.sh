#!/bin/bash
brew install pipx
pipx install virtualenv

#https://github.com/brianmario/mysql2/issues/795
export LDFLAGS="-L/usr/local/opt/openssl/lib"
export CPPFLAGS="-I/usr/local/opt/openssl/include"
./install_connector.sh tap-postgres
./install_connector.sh target-postgres singer-target-postgres


