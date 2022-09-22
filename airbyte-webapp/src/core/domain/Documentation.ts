export const fetchDocumentation = async (url: string): Promise<string> => {
  const response = await fetch(url, {
    method: "GET",
  });

  const contentType = response.headers.get("content-type");

  if (!contentType?.toLowerCase().includes("text/markdown")) {
    throw new Error(`Documentation to be expected text/markdown, was ${contentType}`);
  }

  return await response.text();
};
