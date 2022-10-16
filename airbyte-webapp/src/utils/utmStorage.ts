const UTM_STORAGE_KEY = "utmParams";

export const storeUtmFromQuery = (queryString?: string): void => {
  if (queryString) {
    const queryParams = Array.from(new URLSearchParams(queryString).entries());

    const utmParams = queryParams.filter(([key]) => key.startsWith("utm_"));

    if (utmParams.length) {
      sessionStorage.setItem(UTM_STORAGE_KEY, JSON.stringify(Object.fromEntries(utmParams)));
    }
  }
};

export const getUtmFromStorage = (): Record<string, string> => {
  const utmParams = sessionStorage.getItem(UTM_STORAGE_KEY);
  return utmParams ? JSON.parse(utmParams) : {};
};

export const clearUtmStorage = (): void => {
  localStorage.removeItem(UTM_STORAGE_KEY);
};
