import { DestinationSyncMode, SyncMode } from "core/request/AirbyteClient";

import { SyncSchemaStream } from "../../../core/domain/catalog";
import { getOptimalSyncMode, verifyConfigCursorField, verifySupportedSyncModes } from "./formConfigHelpers";

const mockedStreamNode: SyncSchemaStream = {
  stream: {
    name: "test",
    supportedSyncModes: [],
    jsonSchema: {},
    sourceDefinedCursor: undefined,
    sourceDefinedPrimaryKey: [],
    defaultCursorField: [],
  },
  config: {
    cursorField: [],
    primaryKey: [],
    selected: true,
    syncMode: SyncMode.full_refresh,
    destinationSyncMode: DestinationSyncMode.append,
    aliasName: "",
  },
  id: "1",
};

describe("formConfigHelpers", () => {
  describe("verifySupportedSyncModes", () => {
    const streamNodeWithDefinedSyncMode = {
      ...mockedStreamNode,
      stream: { ...mockedStreamNode.stream, supportedSyncModes: [SyncMode.incremental] },
    } as SyncSchemaStream;

    test("should not change supportedSyncModes if it's not empty", () => {
      const streamNode = verifySupportedSyncModes(streamNodeWithDefinedSyncMode);

      expect(streamNode?.stream?.supportedSyncModes).toStrictEqual([SyncMode.incremental]);
    });

    test("should set default supportedSyncModes if it's empty", () => {
      const streamNodeWithEmptySyncMode = {
        ...streamNodeWithDefinedSyncMode,
        stream: { ...mockedStreamNode.stream, supportedSyncModes: [] },
      } as SyncSchemaStream;
      const streamNode = verifySupportedSyncModes(streamNodeWithEmptySyncMode);

      expect(streamNode?.stream?.supportedSyncModes).toStrictEqual([SyncMode.full_refresh]);
    });
  });

  describe("verifyConfigCursorField", () => {
    const streamWithDefinedCursorField: SyncSchemaStream = {
      ...mockedStreamNode,
      config: { ...mockedStreamNode.config, cursorField: ["id"] },
      stream: { ...mockedStreamNode.stream, defaultCursorField: ["name"] },
    } as SyncSchemaStream;

    test("should leave cursorField value as is if it's defined", () => {
      const streamNode = verifyConfigCursorField(streamWithDefinedCursorField);

      expect(streamNode?.config?.cursorField).toStrictEqual(["id"]);
    });

    test("should set defaultCursorField if cursorField is not defined", () => {
      const streamNodeWithoutDefinedCursor = {
        ...streamWithDefinedCursorField,
        config: { ...mockedStreamNode.config, cursorField: [] },
      } as SyncSchemaStream;
      const streamNode = verifyConfigCursorField(streamNodeWithoutDefinedCursor);

      expect(streamNode?.config?.cursorField).toStrictEqual(["name"]);
    });

    test("should leave cursorField empty if defaultCursorField not defined", () => {
      const streamNode = verifyConfigCursorField(mockedStreamNode);

      expect(streamNode?.config?.cursorField).toStrictEqual([]);
    });
  });

  describe("getOptimalSyncMode", () => {
    test("should get 'Incremental(cursor defined) => Append dedup' mode", () => {
      const streamNodeWithIncrDedupMode = {
        ...mockedStreamNode,
        stream: { ...mockedStreamNode.stream, supportedSyncModes: [SyncMode.incremental], sourceDefinedCursor: true },
      } as SyncSchemaStream;
      const nodeStream = getOptimalSyncMode(streamNodeWithIncrDedupMode, [DestinationSyncMode.append_dedup]);

      expect(nodeStream?.config?.syncMode).toBe(SyncMode.incremental);
      expect(nodeStream?.config?.destinationSyncMode).toBe(DestinationSyncMode.append_dedup);
    });

    test("should get 'FullRefresh => Overwrite' mode", () => {
      const nodeStream = getOptimalSyncMode(mockedStreamNode, [DestinationSyncMode.overwrite]);

      expect(nodeStream?.config?.syncMode).toBe(SyncMode.full_refresh);
      expect(nodeStream?.config?.destinationSyncMode).toBe(DestinationSyncMode.overwrite);
    });

    test("should get 'Incremental => Append' mode", () => {
      const streamNodeWithIncrAppendMode = {
        ...mockedStreamNode,
        stream: { ...mockedStreamNode.stream, supportedSyncModes: [SyncMode.incremental] },
      } as SyncSchemaStream;
      const nodeStream = getOptimalSyncMode(streamNodeWithIncrAppendMode, [DestinationSyncMode.append]);

      expect(nodeStream?.config?.syncMode).toBe(SyncMode.incremental);
      expect(nodeStream?.config?.destinationSyncMode).toBe(DestinationSyncMode.append);
    });

    test("should get 'FullRefresh => Append' mode", () => {
      const nodeStream = getOptimalSyncMode(mockedStreamNode, [DestinationSyncMode.append]);

      expect(nodeStream?.config?.syncMode).toBe(SyncMode.full_refresh);
      expect(nodeStream?.config?.destinationSyncMode).toBe(DestinationSyncMode.append);
    });
    test("should return untouched nodeStream", () => {
      const nodeStream = getOptimalSyncMode(mockedStreamNode, []);

      expect(nodeStream).toBe(mockedStreamNode);
    });
  });
});
