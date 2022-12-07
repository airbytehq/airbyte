import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import dayjs from "dayjs";
import { TestWrapper } from "test-utils/testutils";
import timezoneMock from "timezone-mock";

import { DatePicker, toEquivalentLocalTime } from "./DatePicker";

describe(`${toEquivalentLocalTime.name}`, () => {
  // Seems silly, but dayjs has a bug when formatting years, so this is a useful test:
  // https://github.com/iamkun/dayjs/issues/1745
  it("handles a date in the year 1", () => {
    const TEST_UTC_TIMESTAMP = "0001-12-01T09:00:00Z";

    const result = toEquivalentLocalTime(TEST_UTC_TIMESTAMP);

    expect(result).toEqual(undefined);
  });

  it("handles an invalid date", () => {
    const TEST_UTC_TIMESTAMP = "not a date";

    const result = toEquivalentLocalTime(TEST_UTC_TIMESTAMP);

    expect(result).toEqual(undefined);
  });

  it("outputs the same YYYY-MM-DDTHH:mm:ss", () => {
    timezoneMock.register("Etc/GMT+10");
    const TEST_TIMEZONE_UTC_OFFSET_IN_MINUTES = 600; // corresponds to GMT+10
    const TEST_UTC_TIMESTAMP = "2000-01-01T12:00:00Z";

    const result = toEquivalentLocalTime(TEST_UTC_TIMESTAMP);

    // Regardless of the timezone, the local time should be the same
    expect(dayjs(result).format().substring(0, 19)).toEqual(TEST_UTC_TIMESTAMP.substring(0, 19));
    expect(result?.getTimezoneOffset()).toEqual(TEST_TIMEZONE_UTC_OFFSET_IN_MINUTES);
  });

  it("converts utc time to equivalent local time in PST", () => {
    timezoneMock.register("US/Pacific");
    const TEST_TIMEZONE_UTC_OFFSET_IN_MINUTES = 480; // corresponds to the registered mock timezone
    const TEST_UTC_TIMESTAMP = "2022-01-01T00:00:00Z";

    const expectedDateObject = dayjs
      .utc(TEST_UTC_TIMESTAMP)
      .add(TEST_TIMEZONE_UTC_OFFSET_IN_MINUTES, "minutes")
      .toDate();

    expect(toEquivalentLocalTime(TEST_UTC_TIMESTAMP)).toEqual(expectedDateObject);
  });

  it("converts utc time to equivalent local time in EST", () => {
    timezoneMock.register("US/Eastern");
    const TEST_TIMEZONE_UTC_OFFSET_IN_MINUTES = 300; // corresponds to the registered mock timezone
    const TEST_UTC_TIMESTAMP = "2022-01-01T00:00:00Z";

    const expectedDateObject = dayjs
      .utc(TEST_UTC_TIMESTAMP)
      .add(TEST_TIMEZONE_UTC_OFFSET_IN_MINUTES, "minutes")
      .toDate();

    expect(toEquivalentLocalTime(TEST_UTC_TIMESTAMP)).toEqual(expectedDateObject);
  });

  it("keeps a utc timestamp exactly the same", () => {
    timezoneMock.register("UTC");
    const TEST_UTC_TIMESTAMP = "2022-01-01T00:00:00Z";

    const expectedDateObject = dayjs.utc(TEST_UTC_TIMESTAMP).toDate();

    expect(toEquivalentLocalTime(TEST_UTC_TIMESTAMP)).toEqual(expectedDateObject);
  });

  afterEach(() => {
    // Return global Date() object to system behavior
    timezoneMock.unregister();
  });
});

describe(`${DatePicker.name}`, () => {
  it("allows typing a date manually", async () => {
    const MOCK_DESIRED_DATETIME = "2010-09-12T00:00:00Z";
    let mockValue = "";
    render(
      <TestWrapper>
        <DatePicker
          onChange={(value) => {
            // necessary for controlled inputs https://github.com/testing-library/user-event/issues/387#issuecomment-819868799
            mockValue = mockValue + value;
          }}
          value={mockValue}
        />
      </TestWrapper>
    );

    const input = screen.getByTestId("input");
    await userEvent.type(input, MOCK_DESIRED_DATETIME, { delay: 1 });

    expect(mockValue).toEqual(MOCK_DESIRED_DATETIME);
  });

  it("allows selecting a date from the datepicker", async () => {
    jest.useFakeTimers().setSystemTime(new Date("2010-09-05"));
    const MOCK_DESIRED_DATETIME = "2010-09-12";
    let mockValue = "";
    render(
      <TestWrapper>
        <DatePicker
          onChange={(value) => {
            // necessary for controlled inputs https://github.com/testing-library/user-event/issues/387#issuecomment-819868799
            mockValue = mockValue + value;
          }}
          value={mockValue}
        />
      </TestWrapper>
    );

    const datepicker = screen.getByLabelText("Open datepicker");
    userEvent.click(datepicker);
    const date = screen.getByLabelText("Choose Sunday, September 12th, 2010");
    userEvent.click(date);

    expect(mockValue).toEqual(MOCK_DESIRED_DATETIME);
    jest.useRealTimers();
  });

  it("focuses the input after selecting a date from the datepicker", async () => {
    jest.useFakeTimers().setSystemTime(new Date("2010-09-05"));
    let mockValue = "";
    render(
      <TestWrapper>
        <DatePicker onChange={(value) => (mockValue = value)} value={mockValue} />
      </TestWrapper>
    );

    const datepicker = screen.getByLabelText("Open datepicker");
    userEvent.click(datepicker);
    const date = screen.getByLabelText("Choose Sunday, September 12th, 2010");
    userEvent.click(date);

    const input = screen.getByTestId("input");

    expect(input).toHaveFocus();
    jest.useRealTimers();
  });
});
