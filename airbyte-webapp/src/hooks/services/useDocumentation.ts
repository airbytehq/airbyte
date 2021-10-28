import { useConfig } from "config";
import { UseQueryResult, useQuery } from "react-query";

import { fetchDocumentation } from "core/domain/Documentation";

type UseDocumentationResult = UseQueryResult<string, Error>;

export const documentationKeys = {
  text: (integrationUrl: string) => ["document", integrationUrl] as const,
};

const useDocumentation = (documentationUrl: string): UseDocumentationResult => {
  const { integrationUrl } = useConfig();
  const url =
    documentationUrl.replace("https://docs.airbyte.io", integrationUrl || "/") +
    ".md";

  return useQuery(documentationKeys.text(documentationUrl), () =>
    fetchDocumentation(url)
  );
};

export default useDocumentation;
