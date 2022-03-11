case $1 in

    --read|-r)
        python main.py read --config secrets/config.json --catalog sample_files/configured_catalog.json | sed 's/record.*/record...\"}/'
        ;;
    --state|-s)
        python main.py read --config secrets/config.json --catalog sample_files/configured_catalog.json --state sample_files/state.json | sed 's/record.*/record...\"}/'
        ;;
  *)
    echo "No Input or Invalid Input: please use one of the following:"
    echo "Read: --read | -r"
    echo "Pass state: --state | -s"
    ;;
esac