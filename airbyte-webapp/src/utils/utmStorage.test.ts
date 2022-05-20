import { getUtmFromStorage, storeUtmFromQuery, clearUtmStorage } from "./utmStorage";

describe("utmStorage", () => {
  beforeEach(() => {
    clearUtmStorage();
  });

  it("correctly parses UTM parameters into sessionStorage", () => {
    storeUtmFromQuery("?utm_source=twitter&utm_medium=social&utm_campaign=spring2022");
    const expected = {
      utm_source: "twitter",
      utm_medium: "social",
      utm_campaign: "spring2022",
    };
    expect(JSON.parse(sessionStorage.getItem("utmParams") ?? "")).toEqual(expected);
    expect(getUtmFromStorage()).toEqual(expected);
  });

  it("does ignore non utm parameters", () => {
    storeUtmFromQuery("?utm_source=twitter&foo=bar&utm_campaign=spring2022");
    expect(getUtmFromStorage()).toEqual({
      utm_source: "twitter",
      utm_campaign: "spring2022",
    });
    expect(getUtmFromStorage()).not.toHaveProperty("foo");
  });

  it("does only write to sessionStorage when a utm_parameter is present", () => {
    storeUtmFromQuery("?utm_source=twitter&utm_campaign=spring2022");
    expect(getUtmFromStorage()).toEqual({
      utm_source: "twitter",
      utm_campaign: "spring2022",
    });
    storeUtmFromQuery("?order=desc&field=name");
    // UTM storage should be unchanged
    expect(getUtmFromStorage()).toEqual({
      utm_source: "twitter",
      utm_campaign: "spring2022",
    });
    storeUtmFromQuery("?utm_source=blog&utm_medium=webpage");
    // UTM source should now be updated
    expect(getUtmFromStorage()).toEqual({
      utm_source: "blog",
      utm_medium: "webpage",
    });
  });
});
