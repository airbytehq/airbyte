export const copyToClipboard = (content: string): Promise<void> => {
  return navigator.clipboard.writeText(content);
};
