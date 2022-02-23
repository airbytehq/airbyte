import { useConfig } from "config";
import { UseQueryResult, useQuery } from "react-query";

import { fetchDocumentation } from "core/domain/Documentation";

type UseDocumentationResult = UseQueryResult<string, Error>;

export const documentationKeys = {
  text: (integrationUrl: string) => ["document", integrationUrl] as const,
};

const DOCS_URL = "https://docs.airbyte.io";

const useDocumentation = (documentationUrl: string): UseDocumentationResult => {
  const { integrationUrl } = useConfig();
  const url = documentationUrl.replace(DOCS_URL, integrationUrl) + ".md";

  return useQuery(documentationKeys.text(documentationUrl), () =>
    fetchDocumentation(url)
  );
};

export default useDocumentation;
