import { mockStreamConfiguration } from "test-utils/mock-data/mockAirbyteStreamConfiguration";

import { SyncSchemaField } from "core/domain/catalog";
import { AirbyteStreamConfiguration } from "core/request/AirbyteClient";

import {
  mergeFieldPathArrays,
  toggleFieldInPrimaryKey,
  updatePrimaryKey,
  updateCursorField,
  updateFieldSelected,
  toggleAllFieldsSelected,
} from "./streamConfigHelpers";

const FIELD_ONE: SyncSchemaField = {
  path: ["field_one"],
  cleanedName: "field_one",
  key: "field_one",
  type: "string",
};
const FIELD_TWO: SyncSchemaField = {
  path: ["field_two"],
  cleanedName: "field_two",
  key: "field_two",
  type: "string",
};
const FIELD_THREE: SyncSchemaField = {
  cleanedName: "field_three",
  type: "todo",
  key: "field_three",
  path: ["field_three"],
};

const mockSyncSchemaFields: SyncSchemaField[] = [FIELD_ONE, FIELD_TWO, FIELD_THREE];

describe(`${mergeFieldPathArrays.name}`, () => {
  it("merges two arrays of fieldPaths without duplicates", () => {
    const arr1 = [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }];
    const arr2 = [{ fieldPath: FIELD_TWO.path }, { fieldPath: FIELD_THREE.path }];

    expect(mergeFieldPathArrays(arr1, arr2)).toEqual([
      { fieldPath: FIELD_ONE.path },
      { fieldPath: FIELD_TWO.path },
      { fieldPath: FIELD_THREE.path },
    ]);
  });

  it("merges two arrays of complex fieldPaths without duplicates", () => {
    const arr1 = [
      { fieldPath: [...FIELD_ONE.path, ...FIELD_TWO.path] },
      { fieldPath: [...FIELD_TWO.path, ...FIELD_THREE.path] },
    ];
    const arr2 = [
      { fieldPath: [...FIELD_ONE.path, ...FIELD_TWO.path] },
      { fieldPath: [...FIELD_TWO.path, ...FIELD_THREE.path] },
      { fieldPath: [...FIELD_ONE.path, ...FIELD_THREE.path] },
    ];

    expect(mergeFieldPathArrays(arr1, arr2)).toEqual([
      { fieldPath: [...FIELD_ONE.path, ...FIELD_TWO.path] },
      { fieldPath: [...FIELD_TWO.path, ...FIELD_THREE.path] },
      { fieldPath: [...FIELD_ONE.path, ...FIELD_THREE.path] },
    ]);
  });
});

describe(`${updateCursorField.name}`, () => {
  it("updates the cursor field when field selection is disabled", () => {
    const mockConfig: AirbyteStreamConfiguration = {
      ...mockStreamConfiguration,
      fieldSelectionEnabled: false,
      selectedFields: [],
    };

    const newStreamConfiguration = updateCursorField(mockConfig, FIELD_ONE.path, 3);

    expect(newStreamConfiguration).toEqual({
      cursorField: FIELD_ONE.path,
    });
  });
  describe("when fieldSelection is active", () => {
    it("adds the cursor to selectedFields", () => {
      const mockConfig: AirbyteStreamConfiguration = {
        ...mockStreamConfiguration,
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }],
      };

      const newStreamConfiguration = updateCursorField(mockConfig, FIELD_THREE.path, 100);

      expect(newStreamConfiguration).toEqual({
        cursorField: FIELD_THREE.path,
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }, { fieldPath: FIELD_THREE.path }],
      });
    });

    it("updates the cursor field when only one other field is unselected", () => {
      const mockConfig: AirbyteStreamConfiguration = {
        ...mockStreamConfiguration,
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }],
      };

      const newStreamConfiguration = updateCursorField(mockConfig, FIELD_ONE.path, 3);

      expect(newStreamConfiguration).toEqual({
        cursorField: FIELD_ONE.path,
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }],
      });
    });

    it("updates the cursor field when it is one of many unselected fields", () => {
      const mockConfig: AirbyteStreamConfiguration = {
        ...mockStreamConfiguration,
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }],
      };

      const newStreamConfiguration = updateCursorField(mockConfig, ["new_cursor"], 100);

      expect(newStreamConfiguration).toEqual({
        cursorField: ["new_cursor"],
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }, { fieldPath: ["new_cursor"] }],
      });
    });

    it("disables field selection when the selected cursor is the only unselected field", () => {
      const mockConfig: AirbyteStreamConfiguration = {
        ...mockStreamConfiguration,
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }],
      };

      const newStreamConfiguration = updateCursorField(mockConfig, FIELD_THREE.path, 3);

      expect(newStreamConfiguration).toEqual({
        cursorField: FIELD_THREE.path,
        fieldSelectionEnabled: false,
        selectedFields: [],
      });
    });
  });
});

describe(`${updatePrimaryKey.name}`, () => {
  it("updates the primary key field", () => {
    const mockConfig: AirbyteStreamConfiguration = {
      ...mockStreamConfiguration,
      primaryKey: [FIELD_ONE.path],
    };

    const newStreamConfiguration = updatePrimaryKey(mockConfig, [FIELD_TWO.path], 3);

    expect(newStreamConfiguration).toEqual({
      primaryKey: [FIELD_TWO.path],
    });
  });

  describe("when fieldSelection is active", () => {
    it("adds each piece of the composite primary key to selectedFields", () => {
      const mockConfig: AirbyteStreamConfiguration = {
        ...mockStreamConfiguration,
        primaryKey: [FIELD_ONE.path],
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE.path }],
      };

      const newStreamConfiguration = updatePrimaryKey(mockConfig, [FIELD_TWO.path, FIELD_THREE.path], 100);

      expect(newStreamConfiguration).toEqual({
        primaryKey: [FIELD_TWO.path, FIELD_THREE.path],
        selectedFields: [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }, { fieldPath: FIELD_THREE.path }],
        fieldSelectionEnabled: true,
      });
    });

    it("replaces the primary key when many other field are unselected", () => {
      const mockConfig: AirbyteStreamConfiguration = {
        ...mockStreamConfiguration,
        primaryKey: [],
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }],
      };

      const newStreamConfiguration = updatePrimaryKey(mockConfig, [FIELD_THREE.path], 100);

      expect(newStreamConfiguration).toEqual({
        primaryKey: [FIELD_THREE.path],
        selectedFields: [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }, { fieldPath: FIELD_THREE.path }],
        fieldSelectionEnabled: true,
      });
    });

    it("replaces the primary key when only one other field is unselected", () => {
      const mockConfig: AirbyteStreamConfiguration = {
        ...mockStreamConfiguration,
        primaryKey: [FIELD_ONE.path],
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }],
      };

      const newStreamConfiguration = updatePrimaryKey(mockConfig, [FIELD_TWO.path], 3);

      expect(newStreamConfiguration).toEqual({
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }],
        primaryKey: [FIELD_TWO.path],
      });
    });

    it("disables field selection when the selected primary key is the last unselected field", () => {
      const mockConfig: AirbyteStreamConfiguration = {
        ...mockStreamConfiguration,
        primaryKey: [],
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE.path }],
      };

      const newStreamConfiguration = updatePrimaryKey(mockConfig, [FIELD_TWO.path, FIELD_THREE.path], 3);

      expect(newStreamConfiguration).toEqual({
        primaryKey: [FIELD_TWO.path, FIELD_THREE.path],
        selectedFields: [],
        fieldSelectionEnabled: false,
      });
    });

    it("disables field selection when part of the selected primary key is the last unselected field", () => {
      const mockConfig: AirbyteStreamConfiguration = {
        ...mockStreamConfiguration,
        primaryKey: [FIELD_ONE.path],
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }],
      };

      const newStreamConfiguration = updatePrimaryKey(mockConfig, [FIELD_THREE.path], 3);

      expect(newStreamConfiguration).toEqual({
        primaryKey: [FIELD_THREE.path],
        selectedFields: [],
        fieldSelectionEnabled: false,
      });
    });
  });
});

describe(`${toggleFieldInPrimaryKey.name}`, () => {
  it("adds a new field to the composite primary key", () => {
    const mockConfig: AirbyteStreamConfiguration = {
      ...mockStreamConfiguration,
      primaryKey: [FIELD_ONE.path],
    };

    const newStreamConfiguration = toggleFieldInPrimaryKey(mockConfig, FIELD_TWO.path, 3);

    expect(newStreamConfiguration).toEqual({
      primaryKey: [FIELD_ONE.path, FIELD_TWO.path],
    });
  });

  describe("when fieldSelection is active", () => {
    it("adds the new primary key field to selectedFields", () => {
      const mockConfig: AirbyteStreamConfiguration = {
        ...mockStreamConfiguration,
        primaryKey: [FIELD_ONE.path],
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }],
      };

      const newStreamConfiguration = toggleFieldInPrimaryKey(mockConfig, FIELD_THREE.path, 100);

      expect(newStreamConfiguration).toEqual({
        primaryKey: [FIELD_ONE.path, FIELD_THREE.path],
        selectedFields: [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }, { fieldPath: FIELD_THREE.path }],
        fieldSelectionEnabled: true,
      });
    });

    it("adds the new primary key when only one other field is unselected", () => {
      const mockConfig: AirbyteStreamConfiguration = {
        ...mockStreamConfiguration,
        primaryKey: [],
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }],
      };

      const newStreamConfiguration = toggleFieldInPrimaryKey(mockConfig, FIELD_TWO.path, 3);

      expect(newStreamConfiguration).toEqual({
        primaryKey: [FIELD_TWO.path],
        selectedFields: [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }],
        fieldSelectionEnabled: true,
      });
    });

    it("adds the new primary key when it is one of many unselected fields", () => {
      const mockConfig: AirbyteStreamConfiguration = {
        ...mockStreamConfiguration,
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE.path }],
      };

      const newStreamConfiguration = toggleFieldInPrimaryKey(mockConfig, FIELD_TWO.path, 100);

      expect(newStreamConfiguration).toEqual({
        primaryKey: [FIELD_TWO.path],
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }],
      });
    });

    it("disables field selection when selected primary key is the last unselected field", () => {
      const mockConfig: AirbyteStreamConfiguration = {
        ...mockStreamConfiguration,
        primaryKey: [FIELD_ONE.path],
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }],
      };

      const newStreamConfiguration = toggleFieldInPrimaryKey(mockConfig, FIELD_THREE.path, 3);

      expect(newStreamConfiguration).toEqual({
        primaryKey: [FIELD_ONE.path, FIELD_THREE.path],
        selectedFields: [],
        fieldSelectionEnabled: false,
      });
    });
  });
});

describe(`${updateFieldSelected.name}`, () => {
  it("Adds a field to selectedFields when selected", () => {
    const newStreamConfiguration = updateFieldSelected({
      config: {
        ...mockStreamConfiguration,
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }],
      },
      fieldPath: FIELD_THREE.path,
      isSelected: true,
      numberOfFieldsInStream: 5,
      fields: mockSyncSchemaFields,
    });

    expect(newStreamConfiguration).toEqual({
      fieldSelectionEnabled: true,
      selectedFields: [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }, { fieldPath: FIELD_THREE.path }],
    });
  });

  it("Removes a field to selectedFields when deselected selected", () => {
    const newStreamConfiguration = updateFieldSelected({
      config: {
        ...mockStreamConfiguration,
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }, { fieldPath: FIELD_THREE.path }],
      },
      fieldPath: FIELD_THREE.path,
      isSelected: false,
      numberOfFieldsInStream: 5,
      fields: mockSyncSchemaFields,
    });

    expect(newStreamConfiguration).toEqual({
      fieldSelectionEnabled: true,
      selectedFields: [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }],
    });
  });

  it("Deselects the first field, enabling fieldSelection", () => {
    const newStreamConfiguration = updateFieldSelected({
      config: mockStreamConfiguration,
      fieldPath: FIELD_ONE.path,
      isSelected: false,
      numberOfFieldsInStream: 3,
      fields: mockSyncSchemaFields,
    });

    expect(newStreamConfiguration).toEqual({
      fieldSelectionEnabled: true,
      selectedFields: [{ fieldPath: FIELD_TWO.path }, { fieldPath: FIELD_THREE.path }],
    });
  });

  it("Selects the last unselected field", () => {
    const newStreamConfiguration = updateFieldSelected({
      config: {
        ...mockStreamConfiguration,
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }],
      },
      fieldPath: FIELD_THREE.path,
      isSelected: true,
      numberOfFieldsInStream: 3,
      fields: mockSyncSchemaFields,
    });

    expect(newStreamConfiguration).toEqual({
      fieldSelectionEnabled: false,
      selectedFields: [],
    });
  });
});

describe(`${toggleAllFieldsSelected.name}`, () => {
  it("unselects all fields if field selection was disabled", () => {
    const newStreamConfiguration = toggleAllFieldsSelected({ ...mockStreamConfiguration });
    expect(newStreamConfiguration).toEqual({
      fieldSelectionEnabled: true,
      selectedFields: [],
    });
  });

  it("selects all fields if field selection was enabled", () => {
    const newStreamConfiguration = toggleAllFieldsSelected({
      ...mockStreamConfiguration,
      fieldSelectionEnabled: true,
      selectedFields: [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }, { fieldPath: FIELD_THREE.path }],
    });
    expect(newStreamConfiguration).toEqual({
      fieldSelectionEnabled: false,
      selectedFields: [],
    });
  });

  it("keeps cursor field selected if syncMode is incremental", () => {
    const newStreamConfiguration = toggleAllFieldsSelected({
      ...mockStreamConfiguration,
      fieldSelectionEnabled: false,
      selectedFields: [],
      syncMode: "incremental",
      cursorField: FIELD_ONE.path,
    });

    expect(newStreamConfiguration).toEqual({
      fieldSelectionEnabled: true,
      selectedFields: [{ fieldPath: FIELD_ONE.path }],
    });
  });

  it("keeps primary key fields selected if destinationSyncMode is append_dedup", () => {
    const newStreamConfiguration = toggleAllFieldsSelected({
      ...mockStreamConfiguration,
      fieldSelectionEnabled: false,
      selectedFields: [],
      destinationSyncMode: "append_dedup",
      primaryKey: [FIELD_ONE.path, FIELD_TWO.path],
    });

    expect(newStreamConfiguration).toEqual({
      fieldSelectionEnabled: true,
      selectedFields: [{ fieldPath: FIELD_ONE.path }, { fieldPath: FIELD_TWO.path }],
    });
  });
});
