import { clearSegmentCookie, setSegmentAnonymousId } from "./crossDomainUtils";

describe("Tracking utils", () => {
  beforeEach(() => {
    clearSegmentCookie();
  });

  it("correctly creates the cookie", () => {
    const anonymousId = "anonymousId";
    setSegmentAnonymousId("?ajs_anonymous_id=anonymousId");

    expect(localStorage.getItem("ajs_anonymous_id")).toEqual(JSON.stringify(anonymousId));
  });

  it("only creates the cookie if the param is present", () => {
    setSegmentAnonymousId("?utm_source=twitter&utm_campaign=spring2022");
    expect(localStorage.getItem("ajs_anonymous_id")).toBeNull();
  });
});
