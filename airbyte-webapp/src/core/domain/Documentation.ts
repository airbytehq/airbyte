export const fetchDocumentation = async (url: string): Promise<string> => {
  const response = await fetch(url, {
    method: "GET",
  });

  const contentType = response.headers.get("content-type");

  if (contentType?.toLowerCase().includes("text/html")) {
    throw new Error(`Documentation was text/html and such ignored since markdown couldn't be found.`);
  }

  return await response.text();
};
