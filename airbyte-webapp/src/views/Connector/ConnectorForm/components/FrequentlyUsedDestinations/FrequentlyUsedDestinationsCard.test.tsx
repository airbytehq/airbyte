import { fireEvent, render, waitFor } from "@testing-library/react";
import { IntlProvider } from "react-intl";

import en from "locales/en.json";

import { mockData } from "../../../../../test-utils/mock-data/mockFrequentlyUsedDestinations";
import { FrequentlyUsedConnectorsCard, FrequentlyUsedConnectorsCardProps } from "./FrequentlyUsedDestinationsCard";

const renderFrequentlyUsedConnectorsComponent = (props: FrequentlyUsedConnectorsCardProps) =>
  render(
    <IntlProvider locale="en" messages={en}>
      <FrequentlyUsedConnectorsCard {...props} />
    </IntlProvider>
  );

describe("<FrequentlyUsedDestinations />", () => {
  it("should renders with mock data without crash", () => {
    const component = renderFrequentlyUsedConnectorsComponent({
      connectors: mockData,
      connectorType: "destination",
      onConnectorSelect: jest.fn(),
    });

    expect(component).toMatchSnapshot();
  });

  it("should call provided handler with right param", async () => {
    const handler = jest.fn();
    const { getByText } = renderFrequentlyUsedConnectorsComponent({
      connectors: mockData,
      connectorType: "destination",
      onConnectorSelect: handler,
    });
    fireEvent.click(getByText("BigQuery"));

    await waitFor(() => {
      expect(handler).toHaveBeenCalledTimes(1);
      expect(handler).toHaveBeenCalledWith("2", "BigQuery");
    });
  });
});
