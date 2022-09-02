import Cookies from "js-cookie";

export const setSegmentAnonymousIdCookie = (queryString?: string): void => {
  const queryParams = new URLSearchParams(queryString);
  const ajs_anonymous_id = queryParams.get("ajs_anonymous_id");
  if (ajs_anonymous_id) {
    Cookies.set("ajs_anonymous_id", ajs_anonymous_id);
  }
};

export const clearSegmentCookie = () => {
  Cookies.remove("ajs_anonymous_id");
};
