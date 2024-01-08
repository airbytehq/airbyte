import React from 'react';

// Add additional modules here
import main_docs from "../../../airbyte-lib/docs/generated/airbyte_lib.html";
import caches_docs from "../../../airbyte-lib/docs/generated/airbyte_lib/caches.html";

const docs = {
  "airbyte_lib": main_docs,
  "airbyte_lib.caches": caches_docs,
}


export default function AirbyteLibDefinitions({ module }) {
  return <>
    <div dangerouslySetInnerHTML={{ __html: docs[module] }} />
  </>
}
