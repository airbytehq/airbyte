if [ $# -eq 1 ]
  then
    echo "Dropping state and rerunnig"
    rm secrets/state.json
    echo "" > secrets/data
    echo "{}" > secrets/state.json
fi

python -m main read --config secrets/config.json --catalog secrets/configured.json --state secrets/state.json > secrets/output_tmp

cat secrets/output_tmp | grep STATE | tail -n 1 | jq .state.data > secrets/state.json
cat secrets/output_tmp | grep RECORD >> secrets/data