import { SyncSchema, SyncSchemaStream } from "core/domain/catalog";
import {
  DestinationSyncMode,
  FieldTransformTransformType,
  StreamDescriptor,
  StreamTransformTransformType,
  SyncMode,
} from "core/request/AirbyteClient";

import calculateInitialCatalog from "./calculateInitialCatalog";

const mockSyncSchemaStream: SyncSchemaStream = {
  id: "1",
  stream: {
    sourceDefinedCursor: true,
    defaultCursorField: ["source_cursor"],
    sourceDefinedPrimaryKey: [["new_primary_key"]],
    jsonSchema: {},
    name: "test",
    namespace: "namespace-test",
    supportedSyncModes: [],
  },
  config: {
    destinationSyncMode: DestinationSyncMode.append,
    selected: false,
    syncMode: SyncMode.full_refresh,
    cursorField: ["old_cursor"],
    primaryKey: [["old_primary_key"]],
    aliasName: "",
  },
};

describe("calculateInitialCatalog", () => {
  it("should assign ids to all streams", () => {
    const { id, ...restProps } = mockSyncSchemaStream;

    const values = calculateInitialCatalog(
      {
        streams: [restProps],
      } as unknown as SyncSchema,
      [],
      [],
      false
    );

    values.streams.forEach((stream) => {
      expect(stream).toHaveProperty("id", "0");
    });
  });

  it("should set default 'FullRefresh' if 'supportedSyncModes' in stream is empty(or null)", () => {
    const { config, stream: sourceDefinedStream } = mockSyncSchemaStream;

    const values = calculateInitialCatalog(
      {
        streams: [
          {
            id: "1",
            stream: {
              ...sourceDefinedStream,
              supportedSyncModes: null,
            },
            config,
          },
        ],
      } as unknown as SyncSchema,
      [],
      [],
      false
    );

    values.streams.forEach((stream) => {
      expect(stream).toHaveProperty("stream.supportedSyncModes", [SyncMode.full_refresh]);
    });
  });

  it("should not select Incremental | Append Dedup if no source defined primary key is available", () => {
    const { config, stream: sourceDefinedStream } = mockSyncSchemaStream;

    const values = calculateInitialCatalog(
      {
        streams: [
          {
            id: "1",
            stream: {
              ...sourceDefinedStream,
              name: "test",
              sourceDefinedCursor: true,
              defaultCursorField: ["id"],
              supportedSyncModes: [SyncMode.full_refresh, SyncMode.incremental],
              sourceDefinedPrimaryKey: undefined,
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
              ...sourceDefinedStream,
              name: "test",
              sourceDefinedCursor: true,
              defaultCursorField: ["updated_at"],
              supportedSyncModes: [SyncMode.full_refresh, SyncMode.incremental],
              sourceDefinedPrimaryKey: [],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.append_dedup,
              syncMode: SyncMode.full_refresh,
            },
          },
        ],
      },
      [DestinationSyncMode.append_dedup, DestinationSyncMode.overwrite],
      [],
      false
    );

    values.streams.forEach((stream) => {
      expect(stream).toHaveProperty("config.syncMode", SyncMode.full_refresh);
      expect(stream).toHaveProperty("config.destinationSyncMode", DestinationSyncMode.overwrite);
    });
  });

  it("should select 'Incremental(cursor defined) => Append Dedup'", () => {
    const { config, stream: sourceDefinedStream } = mockSyncSchemaStream;

    const values = calculateInitialCatalog(
      {
        streams: [
          {
            id: "1",
            stream: {
              ...sourceDefinedStream,
              name: "test",
              sourceDefinedCursor: true,
              defaultCursorField: ["id"],
              supportedSyncModes: [SyncMode.full_refresh, SyncMode.incremental],
              sourceDefinedPrimaryKey: [
                ["primary", "field1"],
                ["primary", "field2"],
              ],
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
              ...sourceDefinedStream,
              name: "test",
              sourceDefinedCursor: true,
              defaultCursorField: ["updated_at"],
              supportedSyncModes: [SyncMode.full_refresh, SyncMode.incremental],
              sourceDefinedPrimaryKey: [
                ["primary", "field1"],
                ["primary", "field2"],
              ],
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
              ...sourceDefinedStream,
              name: "test",
              sourceDefinedCursor: true,
              defaultCursorField: ["name"],
              supportedSyncModes: [SyncMode.incremental],
              sourceDefinedPrimaryKey: [
                ["primary", "field1"],
                ["primary", "field2"],
              ],
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
      [],
      false
    );

    values.streams.forEach((stream) => {
      expect(stream).toHaveProperty("config.syncMode", SyncMode.incremental);
      expect(stream).toHaveProperty("config.destinationSyncMode", DestinationSyncMode.append_dedup);
    });
  });

  it("should select 'Full Refresh => Overwrite'", () => {
    const { config, stream: sourceDefinedStream } = mockSyncSchemaStream;

    const values = calculateInitialCatalog(
      {
        streams: [
          {
            id: "1",
            stream: {
              ...sourceDefinedStream,
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
              ...sourceDefinedStream,
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
              ...sourceDefinedStream,
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
      [],
      false
    );

    values.streams.forEach((stream) => {
      expect(stream).toHaveProperty("config.syncMode", SyncMode.full_refresh);
      expect(stream).toHaveProperty("config.destinationSyncMode", DestinationSyncMode.overwrite);
    });
  });

  it("should select 'Incremental => Append'", () => {
    const { config, stream: sourceDefinedStream } = mockSyncSchemaStream;

    const values = calculateInitialCatalog(
      {
        streams: [
          {
            id: "1",
            stream: {
              ...sourceDefinedStream,
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
              ...sourceDefinedStream,
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
              ...sourceDefinedStream,
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
      [],
      false
    );

    values.streams.forEach((stream) => {
      expect(stream).toHaveProperty("config.syncMode", SyncMode.incremental);
      expect(stream).toHaveProperty("config.destinationSyncMode", DestinationSyncMode.append);
    });
  });

  it("should select 'Full Refresh => Append'", () => {
    const { config, stream: sourceDefinedStream } = mockSyncSchemaStream;

    const values = calculateInitialCatalog(
      {
        streams: [
          {
            id: "1",
            stream: {
              ...sourceDefinedStream,
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
              ...sourceDefinedStream,
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
              ...sourceDefinedStream,
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
      [],
      false
    );

    values.streams.forEach((stream) => {
      expect(stream).toHaveProperty("config.syncMode", SyncMode.full_refresh);
      expect(stream).toHaveProperty("config.destinationSyncMode", DestinationSyncMode.append);
    });
  });

  it("should not change syncMode, destinationSyncMode in EditMode", () => {
    const { config, stream: sourceDefinedStream } = mockSyncSchemaStream;

    const { streams: calculatedStreams } = calculateInitialCatalog(
      {
        streams: [
          {
            id: "1",
            stream: {
              ...sourceDefinedStream,
              name: "test",
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
      [],
      true
    );

    expect(calculatedStreams[0]).toHaveProperty("stream.supportedSyncModes", [SyncMode.full_refresh]);

    expect(calculatedStreams[0]).toHaveProperty("config.syncMode", SyncMode.full_refresh);
    expect(calculatedStreams[0]).toHaveProperty("config.destinationSyncMode", DestinationSyncMode.append);
  });

  it("should set the default cursorField value when it's available and no cursorField is selected", () => {
    const { stream: sourceDefinedStream, config } = mockSyncSchemaStream;

    const { streams: calculatedStreams } = calculateInitialCatalog(
      {
        streams: [
          {
            id: "1",
            stream: {
              ...sourceDefinedStream,
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
              ...sourceDefinedStream,
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
              ...sourceDefinedStream,
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
      [],
      false
    );

    expect(calculatedStreams[0]).toHaveProperty("config.cursorField", ["default_path"]);
    expect(calculatedStreams[1]).toHaveProperty("config.cursorField", ["selected_path"]);
    expect(calculatedStreams[2]).toHaveProperty("config.cursorField", []);
  });

  it("source defined properties should override the saved properties", () => {
    const { stream: sourceDefinedStream, config } = mockSyncSchemaStream;

    const { streams: calculatedStreams } = calculateInitialCatalog(
      {
        streams: [
          {
            id: "1",
            stream: {
              ...sourceDefinedStream,
              name: "test",
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.append_dedup,
              syncMode: SyncMode.incremental,
            },
          },
        ],
      },
      [DestinationSyncMode.append_dedup],
      [],
      true
    );
    // primary keys
    expect(calculatedStreams[0].stream?.sourceDefinedPrimaryKey).toEqual(sourceDefinedStream?.sourceDefinedPrimaryKey);
    expect(calculatedStreams[0].config?.primaryKey).toEqual(calculatedStreams[0].stream?.sourceDefinedPrimaryKey);

    // cursor field
    expect(calculatedStreams[0].stream?.sourceDefinedCursor).toBeTruthy();
    expect(calculatedStreams[0].stream?.defaultCursorField).toEqual(sourceDefinedStream?.defaultCursorField);
    expect(calculatedStreams[0].config?.cursorField).toEqual(calculatedStreams[0].stream?.defaultCursorField);
  });
  it("should keep original configured primary key if no source-defined primary key", () => {
    const { stream: sourceDefinedStream, config } = mockSyncSchemaStream;

    const { streams: calculatedStreams } = calculateInitialCatalog(
      {
        streams: [
          {
            id: "1",
            stream: {
              ...sourceDefinedStream,
              name: "test",
              sourceDefinedCursor: undefined,
              defaultCursorField: [],
              sourceDefinedPrimaryKey: [],
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
      [],
      false
    );

    expect(calculatedStreams[0].config?.primaryKey).toEqual(config?.primaryKey);
  });
  it("should not override config cursor if sourceDefinedCursor is false", () => {
    const { stream: sourceDefinedStream, config } = mockSyncSchemaStream;

    const { streams: calculatedStreams } = calculateInitialCatalog(
      {
        streams: [
          {
            id: "1",
            stream: {
              ...sourceDefinedStream,
              name: "test",
              sourceDefinedCursor: false,
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.append_dedup,
              syncMode: SyncMode.incremental,
            },
          },
        ],
      },
      [DestinationSyncMode.append_dedup],
      [],
      false
    );

    expect(calculatedStreams[0].config?.cursorField).toEqual(config?.cursorField);
  });
  it("should keep its original config if source-defined primary key matches config primary key", () => {
    const { stream: sourceDefinedStream, config } = mockSyncSchemaStream;

    const { streams: calculatedStreams } = calculateInitialCatalog(
      {
        streams: [
          {
            id: "1",
            stream: {
              ...sourceDefinedStream,
              name: "test",
              sourceDefinedPrimaryKey: [["old_primary_key"]],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.append_dedup,
              syncMode: SyncMode.incremental,
            },
          },
        ],
      },
      [DestinationSyncMode.append_dedup],
      [],
      false
    );

    expect(calculatedStreams[0].config?.primaryKey).toEqual(calculatedStreams[0].stream?.sourceDefinedPrimaryKey);
  });

  it("should not change primary key or cursor if isEditMode is false", () => {
    const { stream: sourceDefinedStream, config } = mockSyncSchemaStream;

    const { streams: calculatedStreams } = calculateInitialCatalog(
      {
        streams: [
          {
            id: "1",
            stream: {
              ...sourceDefinedStream,
              name: "test",
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.append_dedup,
              syncMode: SyncMode.incremental,
            },
          },
        ],
      },
      [DestinationSyncMode.append_dedup],
      [],
      false
    );
    // primary keys
    expect(calculatedStreams[0].config?.primaryKey).toEqual(config?.primaryKey);

    // cursor field
    expect(calculatedStreams[0].config?.cursorField).toEqual(config?.cursorField);
  });

  it("should calculate optimal sync mode if stream is new", () => {
    const { stream: sourceDefinedStream, config } = mockSyncSchemaStream;

    const newStreamDescriptors: StreamDescriptor[] = [{ name: "test", namespace: "namespace-test" }];

    const { streams: calculatedStreams } = calculateInitialCatalog(
      {
        streams: [
          {
            id: "1",
            stream: {
              ...sourceDefinedStream,
              name: "test",
              namespace: "namespace-test",
              sourceDefinedCursor: true,
              defaultCursorField: ["id"],
              supportedSyncModes: [SyncMode.incremental],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.overwrite,
              syncMode: SyncMode.incremental,
            },
          },
          {
            id: "1",
            stream: {
              ...sourceDefinedStream,
              name: "test2",
              namespace: "namespace-test",
              sourceDefinedCursor: true,
              defaultCursorField: ["id"],
              supportedSyncModes: [SyncMode.incremental],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.overwrite,
              syncMode: SyncMode.incremental,
            },
          },
        ],
      },
      [DestinationSyncMode.append_dedup],
      [],
      true,
      newStreamDescriptors
    );

    // new stream has its sync mode calculated
    expect(calculatedStreams[0].config?.syncMode).toEqual(SyncMode.incremental);
    expect(calculatedStreams[0].config?.destinationSyncMode).toEqual(DestinationSyncMode.append_dedup);

    // existing stream remains as-is
    expect(calculatedStreams[1].config?.syncMode).toEqual(SyncMode.incremental);
    expect(calculatedStreams[1].config?.destinationSyncMode).toEqual(DestinationSyncMode.overwrite);
  });

  it("should remove the entire primary key if any path from it was removed", () => {
    const { config, stream: sourceDefinedStream } = mockSyncSchemaStream;
    const values = calculateInitialCatalog(
      {
        streams: [
          {
            id: "1",
            stream: {
              ...sourceDefinedStream,
              name: "test",
              sourceDefinedCursor: true,
              defaultCursorField: ["id"],
              sourceDefinedPrimaryKey: [],
              supportedSyncModes: [SyncMode.incremental],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.append_dedup,
              syncMode: SyncMode.incremental,
              primaryKey: [["id"], ["email"]],
            },
          },
          {
            id: "2",
            stream: {
              ...sourceDefinedStream,
              name: "test-2",
              sourceDefinedCursor: true,
              defaultCursorField: ["updated_at"],
              sourceDefinedPrimaryKey: [],
              supportedSyncModes: [SyncMode.incremental],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.append_dedup,
              syncMode: SyncMode.incremental,
              primaryKey: [["id"]],
            },
          },
        ],
      },
      [DestinationSyncMode.append_dedup],
      [
        {
          transformType: StreamTransformTransformType.update_stream,
          streamDescriptor: { name: "test", namespace: "namespace-test" },
          updateStream: [
            {
              breaking: true,
              transformType: FieldTransformTransformType.remove_field,
              fieldName: ["id"],
            },
          ],
        },
      ],
      true
    );
    expect(values.streams[0].config?.primaryKey).toEqual([]); // was entirely cleared
    expect(values.streams[1].config?.primaryKey).toEqual([["id"]]); // was not affected
  });

  it("should remove cursor from config if the old cursor field was removed, even if there is a default", () => {
    const { config, stream: sourceDefinedStream } = mockSyncSchemaStream;
    const values = calculateInitialCatalog(
      {
        streams: [
          {
            id: "1",
            stream: {
              ...sourceDefinedStream,
              name: "test",
              sourceDefinedCursor: false,
              defaultCursorField: ["id"],
              sourceDefinedPrimaryKey: [],
              supportedSyncModes: [SyncMode.incremental],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.append_dedup,
              syncMode: SyncMode.incremental,
              cursorField: ["updated_at"],
            },
          },
          {
            id: "2",
            stream: {
              ...sourceDefinedStream,
              name: "test-2",
              sourceDefinedCursor: true,
              defaultCursorField: ["updated_at"],
              supportedSyncModes: [SyncMode.incremental],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.append_dedup,
              syncMode: SyncMode.incremental,
              cursorField: ["updated_at"],
              primaryKey: [["id"]],
            },
          },
        ],
      },
      [DestinationSyncMode.append_dedup],
      [
        {
          transformType: StreamTransformTransformType.update_stream,
          streamDescriptor: { name: "test", namespace: "namespace-test" },
          updateStream: [
            {
              breaking: true,
              transformType: FieldTransformTransformType.remove_field,
              fieldName: ["updated_at"],
            },
          ],
        },
      ],
      true
    );
    expect(values.streams[0].config?.cursorField).toEqual([]); // was entirely cleared and not replaced with default
    expect(values.streams[1].config?.cursorField).toEqual(["updated_at"]); // was unaffected
  });
  it("should clear multiple config fields if multiple fields were removed", () => {
    const { config, stream: sourceDefinedStream } = mockSyncSchemaStream;
    const values = calculateInitialCatalog(
      {
        streams: [
          {
            id: "1",
            stream: {
              ...sourceDefinedStream,
              name: "test",
              sourceDefinedCursor: false,
              defaultCursorField: ["id"],
              sourceDefinedPrimaryKey: [],
              supportedSyncModes: [SyncMode.incremental],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.append_dedup,
              syncMode: SyncMode.incremental,
              cursorField: ["updated_at"],
              primaryKey: [["primary_key"], ["another_field"]],
            },
          },
          {
            id: "2",
            stream: {
              ...sourceDefinedStream,
              name: "test-2",
              sourceDefinedCursor: true,
              defaultCursorField: ["updated_at"],
              sourceDefinedPrimaryKey: [],
              supportedSyncModes: [SyncMode.incremental],
            },
            config: {
              ...config,
              destinationSyncMode: DestinationSyncMode.append_dedup,
              syncMode: SyncMode.incremental,
              cursorField: ["updated_at"],
              primaryKey: [["id"]],
            },
          },
        ],
      },
      [DestinationSyncMode.append_dedup],
      [
        {
          transformType: StreamTransformTransformType.update_stream,
          streamDescriptor: { name: "test", namespace: "namespace-test" },
          updateStream: [
            {
              breaking: true,
              transformType: FieldTransformTransformType.remove_field,
              fieldName: ["updated_at"],
            },
            {
              breaking: true,
              transformType: FieldTransformTransformType.remove_field,
              fieldName: ["primary_key"],
            },
          ],
        },
      ],
      true
    );
    expect(values.streams[0].config?.primaryKey).toEqual([]); // was entirely cleared and not replaced with default
    expect(values.streams[0].config?.cursorField).toEqual([]); // was entirely cleared and not replaced with default

    expect(values.streams[1].config?.primaryKey).toEqual([["id"]]); // was unaffected})
    expect(values.streams[1].config?.cursorField).toEqual(["updated_at"]); // was unaffected})
  });
});
