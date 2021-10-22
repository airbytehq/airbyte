import { SourceDefinitionSpecification } from "../domain/connector";

export const fetchDocumentation = async (
  spec: SourceDefinitionSpecification,
  integrationUrl?: string
): Promise<string> => {
  const url =
    spec.documentationUrl.replace(
      "https://docs.airbyte.io",
      integrationUrl || "/"
    ) + ".md";

  const response = await fetch(url, {
    method: "GET",
  });

  return await response.text();
};
