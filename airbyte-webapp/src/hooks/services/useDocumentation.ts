import { UseQueryResult, useQuery } from "react-query";

import { useConfig } from "config";
import { fetchDocumentation } from "core/domain/Documentation";

import { useExperiment } from "./Experiment";

type UseDocumentationResult = UseQueryResult<string, Error>;

export const documentationKeys = {
  text: (integrationUrl: string) => ["document", integrationUrl] as const,
};

const DOCS_URL = /^https:\/\/docs\.airbyte\.(io|com)/;

const AVAILABLE_INAPP_DOCS = ["hubspot", "facebook-marketing"];

export const useDocumentation = (documentationUrl: string): UseDocumentationResult => {
  const { integrationUrl } = useConfig();
  const shortSetupGuides = useExperiment("connector.shortSetupGuides", false);
  const docName = documentationUrl.substring(documentationUrl.lastIndexOf("/") + 1);
  const showShortSetupGuide = shortSetupGuides && AVAILABLE_INAPP_DOCS.includes(docName);
  const url = `${documentationUrl.replace(DOCS_URL, integrationUrl)}${showShortSetupGuide ? ".inapp.md" : ".md"}`;

  return useQuery(documentationKeys.text(documentationUrl), () => fetchDocumentation(url), {
    enabled: !!documentationUrl,
    refetchOnMount: false,
    refetchOnWindowFocus: false,
    retry: false,
  });
};
