import { isGdprCountry } from "./dataPrivacy";

const mockTimeZone = (timeZone: string) => {
  jest.spyOn(Intl, "DateTimeFormat").mockImplementation(
    () =>
      ({
        resolvedOptions: () =>
          ({
            timeZone,
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
          } as any),
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
      } as any)
  );
};

describe("dataPrivacy", () => {
  describe("isGdprCountry()", () => {
    afterEach(() => {
      jest.clearAllMocks();
    });

    it("should return true for timezones inside EU", () => {
      mockTimeZone("Europe/Berlin");
      expect(isGdprCountry()).toBe(true);
    });

    it("should return false for non EU countries", () => {
      mockTimeZone("America/Chicago");
      expect(isGdprCountry()).toBe(false);
    });
  });
});
