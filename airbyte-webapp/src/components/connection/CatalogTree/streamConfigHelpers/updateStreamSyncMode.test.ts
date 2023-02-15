import { mockAirbyteStream } from "test-utils/mock-data/mockAirbyteStream";
import { mockStreamConfiguration } from "test-utils/mock-data/mockAirbyteStreamConfiguration";

import { updateStreamSyncMode } from "./updateStreamSyncMode";
import { SyncModeValue } from "../next/SyncModeSelect";

describe(`${updateStreamSyncMode.name}`, () => {
  it("updates the sync modes", () => {
    const syncModes: SyncModeValue = {
      syncMode: "full_refresh",
      destinationSyncMode: "overwrite",
    };
    expect(updateStreamSyncMode(mockAirbyteStream, mockStreamConfiguration, syncModes)).toEqual(
      expect.objectContaining({ ...syncModes })
    );
  });

  describe("when fieldSelection is enabled", () => {
    const PK_PART_ONE = ["pk_part_one"];
    const PK_PART_TWO = ["pk_part_two"];
    const DEFAULT_CURSOR_FIELD_PATH = ["default_cursor"];
    const DEFAULT_PRIMARY_KEY = [PK_PART_ONE, PK_PART_TWO];
    const UNRELATED_FIELD_PATH = ["unrelated_field_path"];

    it("does not add default pk or cursor for irrelevant sync modes", () => {
      const syncModes: SyncModeValue = {
        syncMode: "full_refresh",
        destinationSyncMode: "overwrite",
      };
      const updatedConfig = updateStreamSyncMode(
        {
          ...mockAirbyteStream,
          sourceDefinedCursor: true,
          defaultCursorField: DEFAULT_CURSOR_FIELD_PATH,
          sourceDefinedPrimaryKey: DEFAULT_PRIMARY_KEY,
        },
        mockStreamConfiguration,
        syncModes
      );

      expect(updatedConfig).toEqual(
        expect.objectContaining({
          fieldSelectionEnabled: false,
          selectedFields: [],
          ...syncModes,
        })
      );
    });

    it("automatically selects the default cursor", () => {
      const syncModes: SyncModeValue = {
        syncMode: "incremental",
        destinationSyncMode: "append",
      };

      const updatedConfig = updateStreamSyncMode(
        { ...mockAirbyteStream, sourceDefinedCursor: true, defaultCursorField: DEFAULT_CURSOR_FIELD_PATH },
        {
          ...mockStreamConfiguration,
          fieldSelectionEnabled: true,
          selectedFields: [{ fieldPath: UNRELATED_FIELD_PATH }],
        },
        syncModes
      );

      expect(updatedConfig).toEqual(
        expect.objectContaining({
          ...syncModes,
          selectedFields: [{ fieldPath: UNRELATED_FIELD_PATH }, { fieldPath: DEFAULT_CURSOR_FIELD_PATH }],
        })
      );
    });

    it("automatically selects the composite primary key fields", () => {
      const syncModes: SyncModeValue = {
        syncMode: "incremental",
        destinationSyncMode: "append_dedup",
      };

      const updatedConfig = updateStreamSyncMode(
        { ...mockAirbyteStream, sourceDefinedPrimaryKey: DEFAULT_PRIMARY_KEY },
        {
          ...mockStreamConfiguration,
          fieldSelectionEnabled: true,
          selectedFields: [{ fieldPath: UNRELATED_FIELD_PATH }],
        },
        syncModes
      );

      expect(updatedConfig).toEqual(
        expect.objectContaining({
          ...syncModes,
          selectedFields: [{ fieldPath: UNRELATED_FIELD_PATH }, { fieldPath: PK_PART_ONE }, { fieldPath: PK_PART_TWO }],
        })
      );
    });
  });
});
