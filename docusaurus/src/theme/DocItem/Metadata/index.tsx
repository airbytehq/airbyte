/**
 * Wraps @docusaurus/theme-classic DocItem/Metadata.
 *
 * Adds `og:type=article` on docs pages. The theme only emits og:type for blog
 * posts; the site-wide default (`website`) is set in themeConfig.metadata and
 * is overridden here because this <Head> renders after SiteMetadata.
 */

import React, {type ReactNode} from 'react';
import Head from '@docusaurus/Head';
import Metadata from '@theme-original/DocItem/Metadata';
import type MetadataType from '@theme/DocItem/Metadata';
import type {WrapperProps} from '@docusaurus/types';

type Props = WrapperProps<typeof MetadataType>;

export default function MetadataWrapper(props: Props): ReactNode {
  return (
    <>
      <Metadata {...props} />
      <Head>
        <meta property="og:type" content="article" />
      </Head>
    </>
  );
}
