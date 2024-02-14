import React from 'react';

// Add additional modules here
import api_reference_home from "../../../airbyte-lib/docs/generated/airbyte_lib.html";
import caches_docs from "../../../airbyte-lib/docs/generated/airbyte_lib/caches.html";
import datasets_docs from "../../../airbyte-lib/docs/generated/airbyte_lib/caches.html";

const docs = {
  "airbyte_lib": api_reference_home,
  "airbyte_lib.caches": caches_docs,
  "airbyte_lib.datasets": datasets_docs,
}

export default function AirbyteLibModuleReference({ module }) {
  return <>
    <div dangerouslySetInnerHTML={{ __html: modules[module] }} />
  </>
}
;
