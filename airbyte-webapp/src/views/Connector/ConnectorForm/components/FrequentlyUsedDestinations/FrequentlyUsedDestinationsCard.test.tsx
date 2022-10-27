import { fireEvent, render, waitFor } from "@testing-library/react";
import { IntlProvider } from "react-intl";

import en from "locales/en.json";

import { mockData } from "../../../../../test-utils/mock-data/mockFrequentlyUsedDestinations";
import { FrequentlyUsedDestinationsCard, FrequentlyUsedDestinationsCardProps } from "./FrequentlyUsedDestinationsCard";

const renderFrequentlyUsedDestinationsComponent = (props: FrequentlyUsedDestinationsCardProps) =>
  render(
    <IntlProvider locale="en" messages={en}>
      <FrequentlyUsedDestinationsCard {...props} />
    </IntlProvider>
  );

describe("<FrequentlyUsedDestinations />", () => {
  it("should renders with mock data without crash", () => {
    const component = renderFrequentlyUsedDestinationsComponent({
      destinations: mockData,
      onDestinationSelect: jest.fn(),
    });

    expect(component).toMatchSnapshot();
  });

  it("should call provided handler with right param", async () => {
    const handler = jest.fn();
    const { getByText } = renderFrequentlyUsedDestinationsComponent({
      destinations: mockData,
      onDestinationSelect: handler,
    });
    fireEvent.click(getByText("BigQuery"));

    await waitFor(() => {
      expect(handler).toHaveBeenCalledTimes(1);
      expect(handler).toHaveBeenCalledWith("2", "BigQuery");
    });
  });
});
