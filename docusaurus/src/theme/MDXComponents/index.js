import React from 'react';
// Import the original mapper
import MDXComponents from '@theme-original/MDXComponents';
import { AppliesTo } from '@site/src/components/AppliesTo';
import { FieldAnchor } from '@site/src/components/FieldAnchor';

export default {
  // Re-use the default mapping
  ...MDXComponents,
  AppliesTo,
  FieldAnchor
};