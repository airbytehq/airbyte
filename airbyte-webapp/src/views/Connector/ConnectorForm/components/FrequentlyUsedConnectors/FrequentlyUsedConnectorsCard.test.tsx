import { fireEvent, render, waitFor } from "@testing-library/react";
import { mockDestinationsData } from "test-utils/mock-data/mockFrequentlyUsedDestinations";
import { TestWrapper } from "test-utils/testutils";

import { FrequentlyUsedConnectorsCard, FrequentlyUsedConnectorsCardProps } from "./FrequentlyUsedConnectorsCard";

const renderFrequentlyUsedConnectorsComponent = (props: FrequentlyUsedConnectorsCardProps) =>
  render(
    <TestWrapper>
      <FrequentlyUsedConnectorsCard {...props} />
    </TestWrapper>
  );

describe("<mockFrequentlyUsedConnectors />", () => {
  it("should renders with mock data without crash", () => {
    const component = renderFrequentlyUsedConnectorsComponent({
      connectors: mockDestinationsData,
      connectorType: "destination",
      onConnectorSelect: jest.fn(),
    });

    expect(component).toMatchSnapshot();
  });

  it("should call provided handler with right param", async () => {
    const handler = jest.fn();
    const { getByText } = renderFrequentlyUsedConnectorsComponent({
      connectors: mockDestinationsData,
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
