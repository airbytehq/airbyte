import React from 'react';
// Import the original mapper
import MDXComponents from '@theme-original/MDXComponents';
import { AppliesTo } from '@site/src/components/AppliesTo';

export default {
  // Re-use the default mapping
  ...MDXComponents,
  AppliesTo,
};