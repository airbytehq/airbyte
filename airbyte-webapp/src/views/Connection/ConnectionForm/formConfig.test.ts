import { DestinationSyncMode, SyncMode, SyncSchema, SyncSchemaStream } from "core/domain/catalog";

import { calculateInitialCatalog } from "./formConfig";

const mockSyncSchemaStream: SyncSchemaStream = {
  id: "1",
  stream: {
    sourceDefinedCursor: null,
    defaultCursorField: [],
    sourceDefinedPrimaryKey: [],
    jsonSchema: {},
    name: "name",
    supportedSyncModes: [],
  },
  config: {
    destinationSyncMode: DestinationSyncMode.Append,
    selected: false,
    syncMode: SyncMode.FullRefresh,
    cursorField: [],
    primaryKey: [],
    aliasName: "",
  },
};

describe("calculateInitialCatalog", () => {
  test("should assign ids to all streams", () => {
    const { id, ...restProps } = mockSyncSchemaStream;

    const values = calculateInitialCatalog(
      {
        streams: [restProps],
      } as unknown as SyncSchema,
      [],
      false
    );

    values.streams.forEach((stream) => {
      expect(stream).toHaveProperty("id", "0");
    });
  });

  test("should set default 'FullRefresh' if 'supportedSyncModes' in stream is empty(or null)", () => {
    const { config, stream } = mockSyncSchemaStream;

    const values = calculateInitialCatalog(
      {
        streams: [
          {
            id: "1",
            stream: {
              ...stream,
              supportedSyncModes: null,
            },
            config,
          },
        ],
      } as unknown as SyncSchema,
      [],
      false
    );

    values.streams.forEach((stream) => {
      expect(stream).toHaveProperty("stream.supportedSyncModes", [SyncMode.FullRefresh]);
    });
  });

  test("should select 'Incremental(cursor defined) => Append Dedup'", () => {
    const { config, stream } = mockSyncSchemaStream;

    const values = calculateInitialCatalog(
      {
        streams: [
          {
            id: "1",
            stream: {
              ...stream,
              sourceDefinedCursor: true,
              defaultCursorField: ["id"],
              supportedSyncModes: [SyncMode.Incremental],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.Overwrite,
              syncMode: SyncMode.FullRefresh,
            },
          },
          {
            id: "2",
            stream: {
              ...stream,
              sourceDefinedCursor: true,
              defaultCursorField: ["updated_at"],
              supportedSyncModes: [SyncMode.Incremental],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.Dedupted,
              syncMode: SyncMode.FullRefresh,
            },
          },
          {
            id: "3",
            stream: {
              ...stream,
              sourceDefinedCursor: true,
              defaultCursorField: ["name"],
              supportedSyncModes: [SyncMode.Incremental],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.Append,
              syncMode: SyncMode.FullRefresh,
            },
          },
        ],
      },
      [DestinationSyncMode.Dedupted],
      false
    );

    values.streams.forEach((stream) => {
      expect(stream).toHaveProperty("config.syncMode", SyncMode.Incremental);
      expect(stream).toHaveProperty("config.destinationSyncMode", DestinationSyncMode.Dedupted);
    });
  });

  test("should select 'Full Refresh => Overwrite'", () => {
    const { config, stream } = mockSyncSchemaStream;

    const values = calculateInitialCatalog(
      {
        streams: [
          {
            id: "1",
            stream: {
              ...stream,
              supportedSyncModes: [SyncMode.Incremental],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.Overwrite,
              syncMode: SyncMode.Incremental,
            },
          },
          {
            id: "2",
            stream: {
              ...stream,
              supportedSyncModes: [SyncMode.Incremental],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.Dedupted,
              syncMode: SyncMode.FullRefresh,
            },
          },
          {
            id: "3",
            stream: {
              ...stream,
              supportedSyncModes: [SyncMode.Incremental],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.Append,
              syncMode: SyncMode.FullRefresh,
            },
          },
        ],
      },
      [DestinationSyncMode.Overwrite],
      false
    );

    values.streams.forEach((stream) => {
      expect(stream).toHaveProperty("config.syncMode", SyncMode.FullRefresh);
      expect(stream).toHaveProperty("config.destinationSyncMode", DestinationSyncMode.Overwrite);
    });
  });

  test("should select 'Incremental => Append'", () => {
    const { config, stream } = mockSyncSchemaStream;

    const values = calculateInitialCatalog(
      {
        streams: [
          {
            id: "1",
            stream: {
              ...stream,
              supportedSyncModes: [SyncMode.Incremental],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.Overwrite,
              syncMode: SyncMode.Incremental,
            },
          },
          {
            id: "2",
            stream: {
              ...stream,
              supportedSyncModes: [SyncMode.Incremental],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.Dedupted,
              syncMode: SyncMode.FullRefresh,
            },
          },
          {
            id: "3",
            stream: {
              ...stream,
              supportedSyncModes: [SyncMode.Incremental],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.Append,
              syncMode: SyncMode.FullRefresh,
            },
          },
        ],
      },
      [DestinationSyncMode.Append],
      false
    );

    values.streams.forEach((stream) => {
      expect(stream).toHaveProperty("config.syncMode", SyncMode.Incremental);
      expect(stream).toHaveProperty("config.destinationSyncMode", DestinationSyncMode.Append);
    });
  });

  test("should select 'Full Refresh => Append'", () => {
    const { config, stream } = mockSyncSchemaStream;

    const values = calculateInitialCatalog(
      {
        streams: [
          {
            id: "1",
            stream: {
              ...stream,
              supportedSyncModes: [SyncMode.FullRefresh],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.Overwrite,
              syncMode: SyncMode.Incremental,
            },
          },
          {
            id: "2",
            stream: {
              ...stream,
              supportedSyncModes: [SyncMode.FullRefresh],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.Dedupted,
              syncMode: SyncMode.Incremental,
            },
          },
          {
            id: "3",
            stream: {
              ...stream,
              supportedSyncModes: [SyncMode.FullRefresh],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.Append,
              syncMode: SyncMode.Incremental,
            },
          },
        ],
      },
      [DestinationSyncMode.Append],
      false
    );

    values.streams.forEach((stream) => {
      expect(stream).toHaveProperty("config.syncMode", SyncMode.FullRefresh);
      expect(stream).toHaveProperty("config.destinationSyncMode", DestinationSyncMode.Append);
    });
  });

  test("should not change syncMode, destinationSyncMode and cursorField in EditMode", () => {
    const { config, stream } = mockSyncSchemaStream;

    const { streams } = calculateInitialCatalog(
      {
        streams: [
          {
            id: "1",
            stream: {
              ...stream,
              sourceDefinedCursor: true,
              defaultCursorField: ["id"],
              supportedSyncModes: [],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.Append,
              syncMode: SyncMode.FullRefresh,
            },
          },
        ],
      },
      [DestinationSyncMode.Dedupted],
      true
    );

    expect(streams[0]).toHaveProperty("stream.supportedSyncModes", [SyncMode.FullRefresh]);

    expect(streams[0]).toHaveProperty("config.cursorField", []);
    expect(streams[0]).toHaveProperty("config.syncMode", SyncMode.FullRefresh);
    expect(streams[0]).toHaveProperty("config.destinationSyncMode", DestinationSyncMode.Append);
  });

  test("should set the default cursorField value when it's available and no cursorField is selected", () => {
    const { stream, config } = mockSyncSchemaStream;

    const { streams } = calculateInitialCatalog(
      {
        streams: [
          {
            id: "1",
            stream: {
              ...stream,
              defaultCursorField: ["default_path"],
            },
            config: {
              ...config,
              cursorField: [],
            },
          },
          {
            id: "2",
            stream: {
              ...stream,
              defaultCursorField: ["default_path"],
            },
            config: {
              ...config,
              cursorField: ["selected_path"],
            },
          },
          {
            id: "3",
            stream: {
              ...stream,
              defaultCursorField: [],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.Overwrite,
              cursorField: [],
            },
          },
        ],
      },
      [DestinationSyncMode.Dedupted],
      false
    );

    expect(streams[0]).toHaveProperty("config.cursorField", ["default_path"]);
    expect(streams[1]).toHaveProperty("config.cursorField", ["selected_path"]);
    expect(streams[2]).toHaveProperty("config.cursorField", []);
  });
});
