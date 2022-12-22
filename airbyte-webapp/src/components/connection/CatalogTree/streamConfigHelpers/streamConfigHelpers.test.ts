import { AirbyteStreamConfiguration } from "core/request/AirbyteClient";

import { addFieldToPrimaryKey, updatePrimaryKey, updateCursorField } from "./streamConfigHelpers";

const mockStreamConfiguration: AirbyteStreamConfiguration = {
  fieldSelectionEnabled: false,
  selectedFields: [],
  selected: true,
  syncMode: "full_refresh",
  destinationSyncMode: "overwrite",
};

describe(`${updateCursorField.name}`, () => {
  it("updates the cursor field when field selection is disabled", () => {
    const mockConfig: AirbyteStreamConfiguration = {
      ...mockStreamConfiguration,
      fieldSelectionEnabled: false,
      selectedFields: [],
    };

    const newStreamConfiguration = updateCursorField(mockConfig, ["new_cursor"], 3);

    expect(newStreamConfiguration).toEqual(
      expect.objectContaining({
        cursorField: ["new_cursor"],
      })
    );
  });

  it("updates the cursor field when it is the only unselected field", () => {
    const mockConfig: AirbyteStreamConfiguration = {
      ...mockStreamConfiguration,
      fieldSelectionEnabled: true,
      selectedFields: [{ fieldPath: ["field_one"] }, { fieldPath: ["field_two"] }],
    };

    const newStreamConfiguration = updateCursorField(mockConfig, ["new_cursor"], 3);

    expect(newStreamConfiguration).toEqual(
      expect.objectContaining({
        cursorField: ["new_cursor"],
        fieldSelectionEnabled: false,
        selectedFields: [],
      })
    );
  });

  it("updates the cursor field when it is one of many unselected fields", () => {
    const mockConfig: AirbyteStreamConfiguration = {
      ...mockStreamConfiguration,
      fieldSelectionEnabled: true,
      selectedFields: [{ fieldPath: ["field_one"] }, { fieldPath: ["field_two"] }],
    };

    const newStreamConfiguration = updateCursorField(mockConfig, ["new_cursor"], 100);

    expect(newStreamConfiguration).toEqual(
      expect.objectContaining({
        cursorField: ["new_cursor"],
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: ["field_one"] }, { fieldPath: ["field_two"] }, { fieldPath: ["new_cursor"] }],
      })
    );
  });
});

describe(`${updatePrimaryKey.name}`, () => {
  it("updates the primary key field", () => {
    const mockConfig: AirbyteStreamConfiguration = {
      ...mockStreamConfiguration,
      primaryKey: [["original_pk"]],
    };

    const newStreamConfiguration = updatePrimaryKey(mockConfig, [["new_pk"]], 3);

    expect(newStreamConfiguration).toEqual(
      expect.objectContaining({
        primaryKey: [["new_pk"]],
      })
    );
  });

  it("updates the primary key field when field selection is enabled", () => {
    const mockConfig: AirbyteStreamConfiguration = {
      ...mockStreamConfiguration,
      primaryKey: [["field_one"]],
      fieldSelectionEnabled: true,
      selectedFields: [{ fieldPath: ["field_one"] }],
    };

    const newStreamConfiguration = updatePrimaryKey(mockConfig, [["field_two"]], 3);

    expect(newStreamConfiguration).toEqual(
      expect.objectContaining({
        primaryKey: [["field_two"]],
        selectedFields: [{ fieldPath: ["field_one"] }, { fieldPath: ["field_two"] }],
        fieldSelectionEnabled: true,
      })
    );
  });

  it("adds the selected primary key to selectedFields", () => {
    const mockConfig: AirbyteStreamConfiguration = {
      ...mockStreamConfiguration,
      primaryKey: [],
      fieldSelectionEnabled: true,
      selectedFields: [{ fieldPath: ["field_one"] }, { fieldPath: ["field_two"] }],
    };

    const newStreamConfiguration = updatePrimaryKey(mockConfig, [["field_three"]], 5);

    expect(newStreamConfiguration).toEqual(
      expect.objectContaining({
        primaryKey: [["field_three"]],
        selectedFields: [{ fieldPath: ["field_one"] }, { fieldPath: ["field_two"] }, { fieldPath: ["field_three"] }],
        fieldSelectionEnabled: true,
      })
    );
  });

  it("disables field selection when selected primary key is the last unselected field", () => {
    const mockConfig: AirbyteStreamConfiguration = {
      ...mockStreamConfiguration,
      primaryKey: [["field_one"]],
      fieldSelectionEnabled: true,
      selectedFields: [{ fieldPath: ["field_one"] }, { fieldPath: ["field_two"] }],
    };

    const newStreamConfiguration = updatePrimaryKey(mockConfig, [["field_three"]], 3);

    expect(newStreamConfiguration).toEqual(
      expect.objectContaining({
        primaryKey: [["field_three"]],
        selectedFields: [],
        fieldSelectionEnabled: false,
      })
    );
  });
});

describe(`${addFieldToPrimaryKey.name}`, () => {
  it("adds a new field to the composite primary key", () => {
    const mockConfig: AirbyteStreamConfiguration = {
      ...mockStreamConfiguration,
      primaryKey: [["first_pk_field"]],
    };

    const newStreamConfiguration = addFieldToPrimaryKey(mockConfig, ["second_pk_field"], 3);

    expect(newStreamConfiguration).toEqual(
      expect.objectContaining({
        primaryKey: [["first_pk_field"], ["second_pk_field"]],
      })
    );
  });

  it("adds the new primary key field to selectedFields when field selection is enabled", () => {
    const mockConfig: AirbyteStreamConfiguration = {
      ...mockStreamConfiguration,
      primaryKey: [["field_one"]],
      fieldSelectionEnabled: true,
      selectedFields: [{ fieldPath: ["field_one"] }, { fieldPath: ["field_two"] }],
    };

    const newStreamConfiguration = addFieldToPrimaryKey(mockConfig, ["field_three"], 5);

    expect(newStreamConfiguration).toEqual(
      expect.objectContaining({
        primaryKey: [["field_one"], ["field_three"]],
        selectedFields: [{ fieldPath: ["field_one"] }, { fieldPath: ["field_two"] }, { fieldPath: ["field_three"] }],
        fieldSelectionEnabled: true,
      })
    );
  });

  it("disables field selection when selected primary key is the last unselected field", () => {
    const mockConfig: AirbyteStreamConfiguration = {
      ...mockStreamConfiguration,
      primaryKey: [["field_one"]],
      fieldSelectionEnabled: true,
      selectedFields: [{ fieldPath: ["field_one"] }, { fieldPath: ["field_two"] }],
    };

    const newStreamConfiguration = addFieldToPrimaryKey(mockConfig, ["field_three"], 3);

    expect(newStreamConfiguration).toEqual(
      expect.objectContaining({
        primaryKey: [["field_one"], ["field_three"]],
        selectedFields: [],
        fieldSelectionEnabled: false,
      })
    );
  });
});
