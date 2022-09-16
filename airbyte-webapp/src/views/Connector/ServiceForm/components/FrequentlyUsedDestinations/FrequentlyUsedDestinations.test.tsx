import { fireEvent, render, waitFor } from "@testing-library/react";
import { Formik } from "formik";
import { IntlProvider } from "react-intl";

import en from "locales/en.json";

import { mockData } from "../../../../../test-utils/mock-data/mockFrequentlyUsedDestinations";
import { FrequentlyUsedDestinations, FrequentlyUsedDestinationsProps } from "./FrequentlyUsedDestinations";

const renderFrequentlyUsedDestinationsComponent = (props: FrequentlyUsedDestinationsProps) =>
  render(
    <Formik initialValues={{}} onSubmit={jest.fn()}>
      <IntlProvider locale="en" messages={en}>
        <FrequentlyUsedDestinations {...props} />
      </IntlProvider>
    </Formik>
  );

describe("<FrequentlyUsedDestinations />", () => {
  it("should renders with mock data without crash", () => {
    const { asFragment } = renderFrequentlyUsedDestinationsComponent({
      destinations: mockData,
      onDestinationSelect: jest.fn(),
      propertyPath: "serviceType",
    });

    expect(asFragment()).toMatchSnapshot();
  });

  it("should call provided handler with right param", async () => {
    const handler = jest.fn();
    const { getByText } = renderFrequentlyUsedDestinationsComponent({
      destinations: mockData,
      onDestinationSelect: handler,
      propertyPath: "serviceType",
    });
    fireEvent.click(getByText("BigQuery"));

    await waitFor(() => {
      expect(handler).toHaveBeenCalledTimes(1);
      expect(handler).toHaveBeenCalledWith("2");
    });
  });
});
