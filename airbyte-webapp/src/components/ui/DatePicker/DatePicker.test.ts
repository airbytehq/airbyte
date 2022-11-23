import dayjs from "dayjs";
import timezoneMock from "timezone-mock";

import { toEquivalentLocalTimeInBrowserTimezone } from "./DatePicker";

describe(`${toEquivalentLocalTimeInBrowserTimezone.name}`, () => {
  it("outputs the same YYYY-MM-DDTHH:mm:ss", () => {
    const TEST_UTC_TIMESTAMP = "2000-01-01T12:00:00Z";

    const result = toEquivalentLocalTimeInBrowserTimezone(dayjs(TEST_UTC_TIMESTAMP));

    // Regardless of the timezone, the local time should be the same
    expect(result.toISOString().substring(0, 19)).toEqual(TEST_UTC_TIMESTAMP.substring(0, 19));
  });

  it("converts utc time to equivalent local time in PST", () => {
    timezoneMock.register("US/Pacific");
    const TEST_TIMEZONE_UTC_OFFSET_IN_MINUTES = 480; // corresponds to the timezone-mock
    const TEST_UTC_TIMESTAMP = "2022-01-01T00:00:00Z";

    const dayjsObject = dayjs.utc(TEST_UTC_TIMESTAMP);
    const expectedDateObject = dayjs
      .utc(TEST_UTC_TIMESTAMP)
      .add(TEST_TIMEZONE_UTC_OFFSET_IN_MINUTES, "minutes")
      .toDate();

    expect(toEquivalentLocalTimeInBrowserTimezone(dayjsObject)).toEqual(expectedDateObject);
  });

  it("converts utc time to equivalent local time in EST", () => {
    timezoneMock.register("US/Eastern");
    const TEST_TIMEZONE_UTC_OFFSET_IN_MINUTES = 300; // corresponds to the timezone-mock
    const TEST_UTC_TIMESTAMP = "2022-01-01T00:00:00Z";

    const dayjsObject = dayjs.utc(TEST_UTC_TIMESTAMP);
    const expectedDateObject = dayjs
      .utc(TEST_UTC_TIMESTAMP)
      .add(TEST_TIMEZONE_UTC_OFFSET_IN_MINUTES, "minutes")
      .toDate();

    expect(toEquivalentLocalTimeInBrowserTimezone(dayjsObject)).toEqual(expectedDateObject);
  });

  it("keeps a utc timestamp exactly the same", () => {
    timezoneMock.register("UTC");
    const TEST_UTC_TIMESTAMP = "2022-01-01T00:00:00Z";

    const dayjsObject = dayjs.utc(TEST_UTC_TIMESTAMP);
    const expectedDateObject = dayjs.utc(TEST_UTC_TIMESTAMP).toDate();

    expect(toEquivalentLocalTimeInBrowserTimezone(dayjsObject)).toEqual(expectedDateObject);
  });

  afterEach(() => {
    // Return global Date() object to system behavior
    timezoneMock.unregister();
  });
});
