export const downloadFile = (blob: Blob, name: string) => {
  const element = document.createElement("a");
  element.href = URL.createObjectURL(blob);
  element.download = name;
  document.body.appendChild(element); // Required for this to work in FireFox
  element.click();
  document.body.removeChild(element);
};

export const fileizeString = (name: string) => name.replace(/[^a-z0-9]/gi, "_").toLowerCase();
