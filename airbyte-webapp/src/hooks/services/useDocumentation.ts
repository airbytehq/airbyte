import { UseQueryResult, useQuery } from "react-query";

import { useConfig } from "config";
import { fetchDocumentation } from "core/domain/Documentation";

type UseDocumentationResult = UseQueryResult<string, Error>;

export const documentationKeys = {
  text: (integrationUrl: string) => ["document", integrationUrl] as const,
};

const DOCS_URL = /^https:\/\/docs\.airbyte\.(io|com)/;

export const useDocumentation = (documentationUrl: string): UseDocumentationResult => {
  const { integrationUrl } = useConfig();
  const url = `${documentationUrl.replace(DOCS_URL, integrationUrl)}.md`;

  return useQuery(documentationKeys.text(documentationUrl), () => fetchDocumentation(url), {
    enabled: !!documentationUrl,
    refetchOnMount: false,
    refetchOnWindowFocus: false,
    retry: false,
  });
};
