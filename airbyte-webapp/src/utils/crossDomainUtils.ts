export const setSegmentAnonymousId = (queryString?: string): void => {
  const queryParams = new URLSearchParams(queryString);
  const ajs_anonymous_id = queryParams.get("ajs_anonymous_id");

  if (ajs_anonymous_id) {
    localStorage.setItem("ajs_anonymous_id", JSON.stringify(ajs_anonymous_id));
  }
};

export const clearSegmentCookie = () => {
  localStorage.removeItem("ajs_anonymous_id");
};
