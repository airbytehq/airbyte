import { useConfig } from "config";
import { useMutation, UseMutationResult } from "react-query";

import { SourceDefinitionSpecification } from "core/domain/connector";
import { fetchDocumentation } from "core/resources/Documentation";

type UseDocumentationResult = UseMutationResult<
  string,
  Error,
  SourceDefinitionSpecification
>;

const useDocumentation = (): UseDocumentationResult => {
  const { integrationUrl } = useConfig();

  return useMutation("doc", (spec: SourceDefinitionSpecification) =>
    fetchDocumentation(spec, integrationUrl)
  );
};

export default useDocumentation;
