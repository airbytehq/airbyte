import { renderHook } from "@testing-library/react-hooks";
import { mockConnection, TestWrapper } from "test-utils";
import { mockDestinationDefinition } from "test-utils/mock-data/mockDestination";
import { mockSourceDefinition } from "test-utils/mock-data/mockSource";

import { useDestinationDefinition } from "services/connector/DestinationDefinitionService";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";

import { useFreeConnectorProgram } from "./useFreeConnectorProgram";
import { useIsConnectionFree } from "./useIsConnectionFree";

jest.mock("./useFreeConnectorProgram", () => ({
  useFreeConnectorProgram: jest.fn(() => ({ userDidEnroll: true })),
}));
const mockUseFreeConnectorProgram = useFreeConnectorProgram as unknown as jest.Mock<
  Partial<typeof useFreeConnectorProgram>
>;

jest.mock("services/connector/DestinationDefinitionService", () => ({
  useDestinationDefinition: jest.fn(() => mockDestinationDefinition),
}));
const mockUseSourceDefinition = useSourceDefinition as unknown as jest.Mock<Partial<typeof useSourceDefinition>>;

jest.mock("services/connector/SourceDefinitionService", () => ({
  useSourceDefinition: jest.fn(() => mockSourceDefinition),
}));
const mockUseDestinationDefinition = useDestinationDefinition as unknown as jest.Mock<
  Partial<typeof useDestinationDefinition>
>;

describe(`${useIsConnectionFree.name}`, () => {
  describe("When the user is enrolled", () => {
    it("returns true if the source is alpha", () => {
      mockUseSourceDefinition.mockReturnValueOnce({ ...mockSourceDefinition, releaseStage: "alpha" });
      const { result } = renderHook(() => useIsConnectionFree(mockConnection), { wrapper: TestWrapper });
      expect(result.current).toEqual(true);
    });

    it("returns false if the source and destination are both GA", () => {
      mockUseSourceDefinition.mockReturnValueOnce({ ...mockSourceDefinition, releaseStage: "generally_available" });
      mockUseDestinationDefinition.mockReturnValueOnce({
        ...mockDestinationDefinition,
        releaseStage: "generally_available",
      });
      const { result } = renderHook(() => useIsConnectionFree(mockConnection), { wrapper: TestWrapper });
      expect(result.current).toEqual(false);
    });
  });

  describe("When the user did not enroll", () => {
    it("returns false even if the source is alpha", () => {
      mockUseFreeConnectorProgram.mockReturnValueOnce({ userDidEnroll: false });
      mockUseSourceDefinition.mockReturnValueOnce({ ...mockSourceDefinition, releaseStage: "alpha" });
      const { result } = renderHook(() => useIsConnectionFree(mockConnection), { wrapper: TestWrapper });
      expect(result.current).toEqual(false);
    });
  });
});
