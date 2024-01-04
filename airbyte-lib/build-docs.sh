#!/bin/sh

# public modules
PUBLIC_MODULES="airbyte_lib"

# determine all folders in airbyte_lib that don't start with an underscore and add them to PUBLIC_MODULES
for d in airbyte_lib/*/ ; do
  echo $d
  if [[ $d != "airbyte_lib/_"* ]]; then
    echo "add"
    PUBLIC_MODULES="$PUBLIC_MODULES $d"
  fi
done

pdoc -t docs $PUBLIC_MODULES --no-show-source -o pdoc_docs