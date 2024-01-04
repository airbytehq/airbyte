import React from 'react';
import docs from "../../../airbyte-lib/pdoc_docs/airbyte_lib.html";



export default function AirbyteLibDefinitions() {
  return <>
    <div dangerouslySetInnerHTML={{ __html: docs }} />
  </>
}
