echo "Preparing certs"
mkdir "certs"
mkdir "safe-place"
cockroach cert create-ca --certs-dir=certs --ca-key=safe-place/ca.key
cockroach cert create-node localhost "$HOSTNAME" --certs-dir=certs --ca-key=safe-place/ca.key
cockroach cert create-client root --certs-dir=certs --ca-key=safe-place/ca.key
cockroach cert create-client test_user --certs-dir=certs --ca-key=safe-place/ca.key
echo "Finished preparing certs"

echo "Starting CockroachDB"
nohup sh cockroachdb_test_user.sh &
cockroach start-single-node --certs-dir=certs
