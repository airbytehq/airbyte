export const fetchDocumentation = async (
  documentationUrl: string,
  integrationUrl?: string
): Promise<string> => {
  const url =
    documentationUrl.replace("https://docs.airbyte.io", integrationUrl || "/") +
    ".md";

  const response = await fetch(url, {
    method: "GET",
  });

  return await response.text();
};
