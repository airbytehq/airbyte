import Cookies from "js-cookie";

import { clearSegmentCookie, setSegmentAnonymousIdCookie } from "./cookiesUtils";

describe("utmStorage", () => {
  beforeEach(() => {
    clearSegmentCookie();
  });

  it("correctly creates the cookie", () => {
    const anonymousId = "anonymousId";
    setSegmentAnonymousIdCookie("?ajs_anonymous_id=anonymousId");

    expect(Cookies.get("ajs_anonymous_id")).toEqual(anonymousId);
  });

  it("only creates the cookie if the param is present", () => {
    setSegmentAnonymousIdCookie("?utm_source=twitter&utm_campaign=spring2022");
    expect(Cookies.get("ajs_anonymous_id")).toBeUndefined();
  });
});
