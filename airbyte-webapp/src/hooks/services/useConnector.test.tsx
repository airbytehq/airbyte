import { makeCacheProvider, makeRenderRestHook } from "@rest-hooks/test";
import { act } from "@testing-library/react-hooks";

import useConnector from "./useConnector";
import SourceDefinitionResource from "core/resources/SourceDefinition";
import DestinationDefinitionResource from "core/resources/DestinationDefinition";

jest.mock("hooks/services/useWorkspace", () => ({
  useWorkspace: () => ({
    workspace: {
      workspaceId: "workspaceId",
    },
  }),
}));

const renderRestHook = makeRenderRestHook(makeCacheProvider);
const results = [
  {
    request: SourceDefinitionResource.listShape(),
    params: { workspaceId: "workspaceId" },
    result: {
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
    },
  },
  {
    request: DestinationDefinitionResource.listShape(),
    params: { workspaceId: "workspaceId" },
    result: {
      destinationDefinitions: [
        {
          destinationDefinitionId: "did1",
          latestDockerImageTag: "0.0.2",
          dockerImageTag: "0.0.1",
        },
        {
          destinationDefinitionId: "did2",
          latestDockerImageTag: "",
          dockerImageTag: "0.0.1",
        },
      ],
    },
  },
];

test.skip("should not call sourceDefinition.updateVersion for deprecated call", async () => {
  const { result, waitForNextUpdate } = renderRestHook(() => useConnector(), {
    results,
  });

  // (sourceDefinitionService.update as jest.Mock).mockResolvedValue([]);

  act(() => {
    result.current.updateAllSourceVersions();
  });

  await waitForNextUpdate();

  // expect(sourceDefinitionService.update).toHaveBeenCalledTimes(1);
  // expect(sourceDefinitionService.update).toHaveBeenCalledWith({
  //   dockerImageTag: "0.0.2",
  //   sourceDefinitionId: "sid1",
  // });
});

test.skip("should not call destinationDefinition.updateVersion for deprecated call", async () => {
  const { result, waitForNextUpdate } = renderRestHook(() => useConnector(), {
    results,
  });

  // (destinationDefinitionService.update as jest.Mock).mockResolvedValue([]);

  act(() => {
    result.current.updateAllDestinationVersions();
  });

  await waitForNextUpdate();

  // expect(destinationDefinitionService.update).toHaveBeenCalledTimes(1);
  // expect(destinationDefinitionService.update).toHaveBeenCalledWith({
  //   dockerImageTag: "0.0.2",
  //   destinationDefinitionId: "did1",
  // });
});
