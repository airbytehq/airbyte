import { SyncSchema, SyncSchemaStream } from "core/domain/catalog";
import { DestinationSyncMode, SyncMode } from "core/request/AirbyteClient";

import calculateInitialCatalog from "./calculateInitialCatalog";

const mockSyncSchemaStream: SyncSchemaStream = {
  id: "1",
  stream: {
    sourceDefinedCursor: undefined,
    defaultCursorField: [],
    sourceDefinedPrimaryKey: [],
    jsonSchema: {},
    name: "test",
    supportedSyncModes: [],
  },
  config: {
    destinationSyncMode: DestinationSyncMode.append,
    selected: false,
    syncMode: SyncMode.full_refresh,
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
      expect(stream).toHaveProperty("stream.supportedSyncModes", [SyncMode.full_refresh]);
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
              name: "test",
              sourceDefinedCursor: true,
              defaultCursorField: ["id"],
              supportedSyncModes: [SyncMode.incremental],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.overwrite,
              syncMode: SyncMode.full_refresh,
            },
          },
          {
            id: "2",
            stream: {
              ...stream,
              name: "test",
              sourceDefinedCursor: true,
              defaultCursorField: ["updated_at"],
              supportedSyncModes: [SyncMode.incremental],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.append_dedup,
              syncMode: SyncMode.full_refresh,
            },
          },
          {
            id: "3",
            stream: {
              ...stream,
              name: "test",
              sourceDefinedCursor: true,
              defaultCursorField: ["name"],
              supportedSyncModes: [SyncMode.incremental],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.append,
              syncMode: SyncMode.full_refresh,
            },
          },
        ],
      },
      [DestinationSyncMode.append_dedup],
      false
    );

    values.streams.forEach((stream) => {
      expect(stream).toHaveProperty("config.syncMode", SyncMode.incremental);
      expect(stream).toHaveProperty("config.destinationSyncMode", DestinationSyncMode.append_dedup);
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
              name: "test",
              supportedSyncModes: [SyncMode.incremental],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.overwrite,
              syncMode: SyncMode.incremental,
            },
          },
          {
            id: "2",
            stream: {
              ...stream,
              name: "test",
              supportedSyncModes: [SyncMode.incremental],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.append_dedup,
              syncMode: SyncMode.full_refresh,
            },
          },
          {
            id: "3",
            stream: {
              ...stream,
              name: "test",
              supportedSyncModes: [SyncMode.incremental],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.append,
              syncMode: SyncMode.full_refresh,
            },
          },
        ],
      },
      [DestinationSyncMode.overwrite],
      false
    );

    values.streams.forEach((stream) => {
      expect(stream).toHaveProperty("config.syncMode", SyncMode.full_refresh);
      expect(stream).toHaveProperty("config.destinationSyncMode", DestinationSyncMode.overwrite);
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
              name: "test",
              supportedSyncModes: [SyncMode.incremental],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.overwrite,
              syncMode: SyncMode.incremental,
            },
          },
          {
            id: "2",
            stream: {
              ...stream,
              name: "test",
              supportedSyncModes: [SyncMode.incremental],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.append_dedup,
              syncMode: SyncMode.full_refresh,
            },
          },
          {
            id: "3",
            stream: {
              ...stream,
              name: "test",
              supportedSyncModes: [SyncMode.incremental],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.append,
              syncMode: SyncMode.full_refresh,
            },
          },
        ],
      },
      [DestinationSyncMode.append],
      false
    );

    values.streams.forEach((stream) => {
      expect(stream).toHaveProperty("config.syncMode", SyncMode.incremental);
      expect(stream).toHaveProperty("config.destinationSyncMode", DestinationSyncMode.append);
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
              name: "test",
              supportedSyncModes: [SyncMode.full_refresh],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.overwrite,
              syncMode: SyncMode.incremental,
            },
          },
          {
            id: "2",
            stream: {
              ...stream,
              name: "test",
              supportedSyncModes: [SyncMode.full_refresh],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.append_dedup,
              syncMode: SyncMode.incremental,
            },
          },
          {
            id: "3",
            stream: {
              ...stream,
              name: "test",
              supportedSyncModes: [SyncMode.full_refresh],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.append,
              syncMode: SyncMode.incremental,
            },
          },
        ],
      },
      [DestinationSyncMode.append],
      false
    );

    values.streams.forEach((stream) => {
      expect(stream).toHaveProperty("config.syncMode", SyncMode.full_refresh);
      expect(stream).toHaveProperty("config.destinationSyncMode", DestinationSyncMode.append);
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
              name: "test",
              sourceDefinedCursor: true,
              defaultCursorField: ["id"],
              supportedSyncModes: [],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.append,
              syncMode: SyncMode.full_refresh,
            },
          },
        ],
      },
      [DestinationSyncMode.append_dedup],
      true
    );

    expect(streams[0]).toHaveProperty("stream.supportedSyncModes", [SyncMode.full_refresh]);

    expect(streams[0]).toHaveProperty("config.cursorField", []);
    expect(streams[0]).toHaveProperty("config.syncMode", SyncMode.full_refresh);
    expect(streams[0]).toHaveProperty("config.destinationSyncMode", DestinationSyncMode.append);
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
              name: "test",
              defaultCursorField: ["default_path"],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.overwrite,
              cursorField: [],
              syncMode: SyncMode.full_refresh,
            },
          },
          {
            id: "2",
            stream: {
              ...stream,
              name: "test",
              defaultCursorField: ["default_path"],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.overwrite,
              cursorField: ["selected_path"],
              syncMode: SyncMode.full_refresh,
            },
          },
          {
            id: "3",
            stream: {
              ...stream,
              name: "test",
              defaultCursorField: [],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.overwrite,
              cursorField: [],
              syncMode: SyncMode.full_refresh,
            },
          },
        ],
      },
      [DestinationSyncMode.append_dedup],
      false
    );

    expect(streams[0]).toHaveProperty("config.cursorField", ["default_path"]);
    expect(streams[1]).toHaveProperty("config.cursorField", ["selected_path"]);
    expect(streams[2]).toHaveProperty("config.cursorField", []);
  });
});
