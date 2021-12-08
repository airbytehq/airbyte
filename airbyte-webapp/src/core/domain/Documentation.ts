export const fetchDocumentation = async (url: string): Promise<string> => {
  const response = await fetch(url, {
    method: "GET",
  });

  return await response.text();
};
