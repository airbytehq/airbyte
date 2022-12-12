for directory in ./source-* ; do
  SOURCE_NAME=$(echo "$directory" | sed 's/.\/source-\([A-Za-z]\)/\1/' | tr - _)
  if test -f "$directory/source_$SOURCE_NAME/$SOURCE_NAME.yaml"; then
    cd $directory

    rm -rf .venv
    python -m venv .venv
    source .venv/bin/activate
    # this assumes that if a venv exist, it is up-to-date
    pip install -r requirements.txt > /dev/null 2>&1
    pip install -e ".[tests]" > /dev/null 2>&1
    pip install -e $0 > /dev/null 2>&1

    python main.py spec > /dev/null 2>&1
    ret=$?
    if [ $ret -ne 0 ]; then
      echo "----Error for source $SOURCE_NAME"
    else
      echo "Source $SOURCE_NAME is fine"
    fi

    deactivate
    cd ..
#  else
#    echo "NAY"
  fi
done
