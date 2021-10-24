import { useConfig } from "config";
import { UseQueryResult, useQuery } from "react-query";

import { fetchDocumentation } from "core/resources/Documentation";

type UseDocumentationResult = UseQueryResult<string, Error>;

export const documentationKeys = {
  text: (integrationUrl: string | undefined) =>
    ["document", integrationUrl] as const,
};

const useDocumentation = (
  documentationUrl: string | undefined
): UseDocumentationResult => {
  const { integrationUrl } = useConfig();

  return useQuery(documentationKeys.text(documentationUrl), () =>
    documentationUrl
      ? fetchDocumentation(documentationUrl, integrationUrl)
      : Promise.resolve("")
  );
};

export default useDocumentation;
