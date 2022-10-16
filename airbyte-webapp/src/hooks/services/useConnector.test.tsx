import { act, renderHook } from "@testing-library/react-hooks";

import useConnector from "./useConnector";

jest.mock("services/connector/SourceDefinitionService", () => ({
  useSourceDefinitionList: () => ({
    sourceDefinitions: [
      {
        sourceDefinitionId: "sid1",
        latestDockerImageTag: "0.0.2",
        dockerImageTag: "0.0.1",
      },
      {
        sourceDefinitionId: "sid2",
        latestDockerImageTag: "",
        dockerImageTag: "0.0.1",
      },
    ],
  }),
  useUpdateSourceDefinition: () => ({
    mutateAsync: jest.fn(),
  }),
}));

jest.mock("services/connector/DestinationDefinitionService", () => ({
  useDestinationDefinitionList: () => ({
    destinationDefinitions: [
      {
        destinationDefinitionId: "sid1",
        latestDockerImageTag: "0.0.2",
        dockerImageTag: "0.0.1",
      },
      {
        destinationDefinitionId: "sid2",
        latestDockerImageTag: "",
        dockerImageTag: "0.0.1",
      },
    ],
  }),
  useUpdateDestinationDefinition: () => ({
    mutateAsync: jest.fn(),
  }),
}));

it.skip("should not call sourceDefinition.updateVersion for deprecated call", async () => {
  const { result, waitForNextUpdate } = renderHook(() => useConnector());

  act(() => {
    result.current.updateAllSourceVersions();
  });

  await waitForNextUpdate();
  // expect(updateSourceMock).toHaveBeenCalledTimes(1);
  // expect(updateSourceMock).toHaveBeenCalledWith({
  //   dockerImageTag: "0.0.2",
  //   sourceDefinitionId: "sid1",
  // });
});

it.skip("should not call destinationDefinition.updateVersion for deprecated call", async () => {
  const { result, waitForNextUpdate } = renderHook(() => useConnector());

  act(() => {
    result.current.updateAllDestinationVersions();
  });

  await waitForNextUpdate();
  // expect(updateDestinationMock).toHaveBeenCalledTimes(1);
  // expect(updateDestinationMock).toHaveBeenCalledWith({
  //   dockerImageTag: "0.0.2",
  //   destinationDefinitionId: "did1",
  // });
});
