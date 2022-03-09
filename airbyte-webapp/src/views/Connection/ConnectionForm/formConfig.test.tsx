import {
  AirbyteStreamConfiguration,
  DestinationSyncMode,
  SyncMode,
} from "core/domain/catalog";
import { calculateInitialCatalog } from "./formConfig";

describe("calculateInitialCatalog", () => {
  it("should assign ids to all streams", () => {
    const values = calculateInitialCatalog(
      {
        streams: [
          {
            stream: {
              sourceDefinedCursor: null,
              defaultCursorField: [],
              sourceDefinedPrimaryKey: [],
              jsonSchema: {},
              name: "name",
              supportedSyncModes: [],
            },
            config: {
              destinationSyncMode: DestinationSyncMode.Overwrite,
              selected: false,
              syncMode: SyncMode.FullRefresh,
              cursorField: [],
              primaryKey: [],
              aliasName: "",
            },
          },
        ],
      },
      {
        connectionSpecification: {},
        destinationDefinitionId: "",
        documentationUrl: "",
        supportsDbt: false,
        supportsNormalization: false,
        supportedDestinationSyncModes: [],
      },
      false
    );

    values.streams.forEach((stream) => {
      expect(stream).toHaveProperty("id");
    });
  });

  it("should select append_dedup if destination supports it", () => {
    const values = calculateInitialCatalog(
      {
        streams: [
          {
            stream: {
              sourceDefinedCursor: null,
              defaultCursorField: [],
              sourceDefinedPrimaryKey: [],
              jsonSchema: {},
              name: "name",
              supportedSyncModes: [],
            },
            config: {
              destinationSyncMode: DestinationSyncMode.Overwrite,
              selected: false,
              syncMode: SyncMode.FullRefresh,
              cursorField: [],
              primaryKey: [],
              aliasName: "",
            },
          },
          {
            stream: {
              sourceDefinedCursor: null,
              defaultCursorField: [],
              sourceDefinedPrimaryKey: [],
              jsonSchema: {},
              name: "name",
              supportedSyncModes: [],
            },
            config: {
              destinationSyncMode: DestinationSyncMode.Dedupted,
              selected: false,
              syncMode: SyncMode.FullRefresh,
              cursorField: [],
              primaryKey: [],
              aliasName: "",
            },
          },
          {
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
          },
        ],
      },
      {
        connectionSpecification: {},
        destinationDefinitionId: "",
        documentationUrl: "",
        supportsDbt: false,
        supportsNormalization: false,
        supportedDestinationSyncModes: [DestinationSyncMode.Dedupted],
      },
      false
    );

    values.streams.forEach((stream) =>
      expect(stream).toHaveProperty(
        "config.destinationSyncMode",
        DestinationSyncMode.Dedupted
      )
    );
  });

  it("should not change syncMode and destinationSyncMode in EditMode", () => {
    const { streams } = calculateInitialCatalog(
      {
        streams: [
          {
            stream: {
              sourceDefinedCursor: null,
              defaultCursorField: [],
              sourceDefinedPrimaryKey: [],
              jsonSchema: {},
              name: "name",
              supportedSyncModes: [SyncMode.Incremental],
            },
            config: {
              destinationSyncMode: DestinationSyncMode.Overwrite,
              selected: false,
              syncMode: SyncMode.FullRefresh,
              cursorField: [],
              primaryKey: [],
              aliasName: "",
            },
          },
        ],
      },
      {
        connectionSpecification: {},
        destinationDefinitionId: "",
        documentationUrl: "",
        supportsDbt: false,
        supportsNormalization: false,
        supportedDestinationSyncModes: [DestinationSyncMode.Dedupted],
      },
      true
    );

    expect(streams[0]).toHaveProperty("config.syncMode", SyncMode.FullRefresh);
    expect(streams[0]).toHaveProperty(
      "config.destinationSyncMode",
      DestinationSyncMode.Overwrite
    );
  });

  it("should prefer incremental sync mode", () => {
    const { streams } = calculateInitialCatalog(
      {
        streams: [
          {
            stream: {
              sourceDefinedCursor: null,
              defaultCursorField: [],
              sourceDefinedPrimaryKey: [],
              jsonSchema: {},
              name: "name",
              supportedSyncModes: [SyncMode.Incremental],
            },
            config: {
              destinationSyncMode: DestinationSyncMode.Overwrite,
              selected: false,
              syncMode: SyncMode.FullRefresh,
              cursorField: [],
              primaryKey: [],
              aliasName: "",
            },
          },
          {
            stream: {
              sourceDefinedCursor: null,
              defaultCursorField: [],
              sourceDefinedPrimaryKey: [],
              jsonSchema: {},
              name: "name",
              supportedSyncModes: [SyncMode.Incremental, SyncMode.FullRefresh],
            },
            config: {
              destinationSyncMode: DestinationSyncMode.Overwrite,
              selected: false,
              syncMode: SyncMode.FullRefresh,
              cursorField: [],
              primaryKey: [],
              aliasName: "",
            },
          },
          {
            stream: {
              sourceDefinedCursor: null,
              defaultCursorField: [],
              sourceDefinedPrimaryKey: [],
              jsonSchema: {},
              name: "name",
              supportedSyncModes: [SyncMode.FullRefresh],
            },
            config: {
              destinationSyncMode: DestinationSyncMode.Overwrite,
              selected: false,
              syncMode: SyncMode.FullRefresh,
              cursorField: [],
              primaryKey: [],
              aliasName: "",
            },
          },
        ],
      },
      {
        connectionSpecification: {},
        destinationDefinitionId: "",
        documentationUrl: "",
        supportsDbt: false,
        supportsNormalization: false,
        supportedDestinationSyncModes: [DestinationSyncMode.Dedupted],
      },
      false
    );

    expect(streams[0]).toHaveProperty("config.syncMode", SyncMode.Incremental);
    expect(streams[1]).toHaveProperty("config.syncMode", SyncMode.Incremental);
    expect(streams[2]).toHaveProperty("config.syncMode", SyncMode.FullRefresh);
  });

  it("should assign default value cursorField when it is available and no cursorField is selected", () => {
    const { streams } = calculateInitialCatalog(
      {
        streams: [
          {
            stream: {
              sourceDefinedCursor: null,
              defaultCursorField: ["default_path"],
              sourceDefinedPrimaryKey: [],
              jsonSchema: {},
              name: "name",
              supportedSyncModes: [SyncMode.Incremental],
            },
            config: {
              syncMode: SyncMode.FullRefresh,
              destinationSyncMode: DestinationSyncMode.Overwrite,
              selected: false,
              cursorField: [],
              primaryKey: [],
              aliasName: "",
            },
          },
          {
            stream: {
              sourceDefinedCursor: null,
              defaultCursorField: ["default_path"],
              sourceDefinedPrimaryKey: [],
              jsonSchema: {},
              name: "name",
              supportedSyncModes: [SyncMode.Incremental],
            },
            config: {
              syncMode: SyncMode.FullRefresh,
              destinationSyncMode: DestinationSyncMode.Overwrite,
              selected: false,
              cursorField: ["selected_path"],
              primaryKey: [],
              aliasName: "",
            },
          },
          {
            stream: {
              sourceDefinedCursor: null,
              defaultCursorField: [],
              sourceDefinedPrimaryKey: [],
              jsonSchema: {},
              name: "name",
              supportedSyncModes: [SyncMode.FullRefresh],
            },
            config: {
              syncMode: SyncMode.FullRefresh,
              destinationSyncMode: DestinationSyncMode.Overwrite,
              selected: false,
              cursorField: [],
              primaryKey: [],
              aliasName: "",
            },
          },
        ],
      },
      {
        connectionSpecification: {},
        destinationDefinitionId: "",
        documentationUrl: "",
        supportsDbt: false,
        supportsNormalization: false,
        supportedDestinationSyncModes: [DestinationSyncMode.Dedupted],
      },
      false
    );

    expect(streams[0]).toHaveProperty("config.cursorField", ["default_path"]);
    expect(streams[1]).toHaveProperty("config.cursorField", ["selected_path"]);
    expect(streams[2]).toHaveProperty("config.cursorField", []);
  });

  it("should pick first syncMode when it is somehow nullable", () => {
    const { streams } = calculateInitialCatalog(
      {
        streams: [
          {
            stream: {
              sourceDefinedCursor: null,
              defaultCursorField: [],
              sourceDefinedPrimaryKey: [],
              jsonSchema: {},
              name: "name",
              supportedSyncModes: [SyncMode.FullRefresh],
            },
            config: ({
              destinationSyncMode: DestinationSyncMode.Overwrite,
              selected: false,
              cursorField: [],
              primaryKey: [],
              aliasName: "",
            } as unknown) as AirbyteStreamConfiguration,
          },
        ],
      },
      {
        connectionSpecification: {},
        destinationDefinitionId: "",
        documentationUrl: "",
        supportsDbt: false,
        supportsNormalization: false,
        supportedDestinationSyncModes: [DestinationSyncMode.Dedupted],
      },
      false
    );

    expect(streams[0]).toHaveProperty("config.syncMode", SyncMode.FullRefresh);
  });
});
