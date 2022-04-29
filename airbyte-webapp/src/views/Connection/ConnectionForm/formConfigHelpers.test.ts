import { DestinationSyncMode, SyncMode, SyncSchemaStream } from "../../../core/domain/catalog";
import { getOptimalSyncMode, verifyConfigCursorField, verifySupportedSyncModes } from "./formConfigHelpers";

const mockedStreamNode: SyncSchemaStream = {
  stream: {
    name: "test",
    supportedSyncModes: [],
    jsonSchema: {},
    sourceDefinedCursor: null,
    sourceDefinedPrimaryKey: [],
    defaultCursorField: [],
  },
  config: {
    cursorField: [],
    primaryKey: [],
    selected: true,
    syncMode: SyncMode.FullRefresh,
    destinationSyncMode: DestinationSyncMode.Append,
    aliasName: "",
  },
  id: "1",
};

describe("formConfigHelpers", () => {
  describe("verifySupportedSyncModes", () => {
    const streamNodeWithDefinedSyncMode: SyncSchemaStream = {
      ...mockedStreamNode,
      stream: { ...mockedStreamNode.stream, supportedSyncModes: [SyncMode.Incremental] },
    };

    test("should not change supportedSyncModes if it's not empty", () => {
      const streamNode = verifySupportedSyncModes(streamNodeWithDefinedSyncMode);

      expect(streamNode.stream.supportedSyncModes).toStrictEqual([SyncMode.Incremental]);
    });

    test("should set default supportedSyncModes if it's empty", () => {
      const streamNodeWithEmptySyncMode = {
        ...streamNodeWithDefinedSyncMode,
        stream: { ...mockedStreamNode.stream, supportedSyncModes: [] },
      };
      const streamNode = verifySupportedSyncModes(streamNodeWithEmptySyncMode);

      expect(streamNode.stream.supportedSyncModes).toStrictEqual([SyncMode.FullRefresh]);
    });
  });

  describe("verifyConfigCursorField", () => {
    const streamWithDefinedCursorField: SyncSchemaStream = {
      ...mockedStreamNode,
      config: { ...mockedStreamNode.config, cursorField: ["id"] },
      stream: { ...mockedStreamNode.stream, defaultCursorField: ["name"] },
    };

    test("should leave cursorField value as is if it's defined", () => {
      const streamNode = verifyConfigCursorField(streamWithDefinedCursorField);

      expect(streamNode.config.cursorField).toStrictEqual(["id"]);
    });

    test("should set defaultCursorField if cursorField is not defined", () => {
      const streamNodeWithoutDefinedCursor = {
        ...streamWithDefinedCursorField,
        config: { ...mockedStreamNode.config, cursorField: [] },
      };
      const streamNode = verifyConfigCursorField(streamNodeWithoutDefinedCursor);

      expect(streamNode.config.cursorField).toStrictEqual(["name"]);
    });

    test("should leave cursorField empty if defaultCursorField not defined", () => {
      const streamNode = verifyConfigCursorField(mockedStreamNode);

      expect(streamNode.config.cursorField).toStrictEqual([]);
    });
  });

  describe("getOptimalSyncMode", () => {
    test("should get 'Incremental(cursor defined) => Append dedup' mode", () => {
      const streamNodeWithIncrDedupMode = {
        ...mockedStreamNode,
        stream: { ...mockedStreamNode.stream, supportedSyncModes: [SyncMode.Incremental], sourceDefinedCursor: true },
      };
      const nodeStream = getOptimalSyncMode(streamNodeWithIncrDedupMode, [DestinationSyncMode.Dedupted]);

      expect(nodeStream.config.syncMode).toBe(SyncMode.Incremental);
      expect(nodeStream.config.destinationSyncMode).toBe(DestinationSyncMode.Dedupted);
    });

    test("should get 'FullRefresh => Overwrite' mode", () => {
      const nodeStream = getOptimalSyncMode(mockedStreamNode, [DestinationSyncMode.Overwrite]);

      expect(nodeStream.config.syncMode).toBe(SyncMode.FullRefresh);
      expect(nodeStream.config.destinationSyncMode).toBe(DestinationSyncMode.Overwrite);
    });

    test("should get 'Incremental => Append' mode", () => {
      const streamNodeWithIncrAppendMode = {
        ...mockedStreamNode,
        stream: { ...mockedStreamNode.stream, supportedSyncModes: [SyncMode.Incremental] },
      };
      const nodeStream = getOptimalSyncMode(streamNodeWithIncrAppendMode, [DestinationSyncMode.Append]);

      expect(nodeStream.config.syncMode).toBe(SyncMode.Incremental);
      expect(nodeStream.config.destinationSyncMode).toBe(DestinationSyncMode.Append);
    });

    test("should get 'FullRefresh => Append' mode", () => {
      const nodeStream = getOptimalSyncMode(mockedStreamNode, [DestinationSyncMode.Append]);

      expect(nodeStream.config.syncMode).toBe(SyncMode.FullRefresh);
      expect(nodeStream.config.destinationSyncMode).toBe(DestinationSyncMode.Append);
    });
    test("should return untouched nodeStream", () => {
      const nodeStream = getOptimalSyncMode(mockedStreamNode, []);

      expect(nodeStream).toBe(mockedStreamNode);
    });
  });
});
