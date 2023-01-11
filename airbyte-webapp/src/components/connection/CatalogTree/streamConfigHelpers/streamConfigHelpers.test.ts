import { AirbyteStreamConfiguration } from "core/request/AirbyteClient";

import {
  mergeFieldPathArrays,
  toggleFieldInPrimaryKey,
  updatePrimaryKey,
  updateCursorField,
} from "./streamConfigHelpers";

const mockStreamConfiguration: AirbyteStreamConfiguration = {
  fieldSelectionEnabled: false,
  selectedFields: [],
  selected: true,
  syncMode: "full_refresh",
  destinationSyncMode: "overwrite",
};

const FIELD_ONE = ["field_one"];
const FIELD_TWO = ["field_two"];
const FIELD_THREE = ["field_three"];

describe(`${mergeFieldPathArrays.name}`, () => {
  it("merges two arrays of fieldPaths without duplicates", () => {
    const arr1 = [{ fieldPath: FIELD_ONE }, { fieldPath: FIELD_TWO }];
    const arr2 = [{ fieldPath: FIELD_TWO }, { fieldPath: FIELD_THREE }];

    expect(mergeFieldPathArrays(arr1, arr2)).toEqual([
      { fieldPath: FIELD_ONE },
      { fieldPath: FIELD_TWO },
      { fieldPath: FIELD_THREE },
    ]);
  });

  it("merges two arrays of complex fieldPaths without duplicates", () => {
    const arr1 = [{ fieldPath: [...FIELD_ONE, ...FIELD_TWO] }, { fieldPath: [...FIELD_TWO, ...FIELD_THREE] }];
    const arr2 = [
      { fieldPath: [...FIELD_ONE, ...FIELD_TWO] },
      { fieldPath: [...FIELD_TWO, ...FIELD_THREE] },
      { fieldPath: [...FIELD_ONE, ...FIELD_THREE] },
    ];

    expect(mergeFieldPathArrays(arr1, arr2)).toEqual([
      { fieldPath: [...FIELD_ONE, ...FIELD_TWO] },
      { fieldPath: [...FIELD_TWO, ...FIELD_THREE] },
      { fieldPath: [...FIELD_ONE, ...FIELD_THREE] },
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

    const newStreamConfiguration = updateCursorField(mockConfig, FIELD_ONE, 3);

    expect(newStreamConfiguration).toEqual({
      cursorField: FIELD_ONE,
    });
  });
  describe("when fieldSelection is active", () => {
    it("adds the cursor to selectedFields", () => {
      const mockConfig: AirbyteStreamConfiguration = {
        ...mockStreamConfiguration,
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE }, { fieldPath: FIELD_TWO }],
      };

      const newStreamConfiguration = updateCursorField(mockConfig, FIELD_THREE, 100);

      expect(newStreamConfiguration).toEqual({
        cursorField: FIELD_THREE,
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE }, { fieldPath: FIELD_TWO }, { fieldPath: FIELD_THREE }],
      });
    });

    it("updates the cursor field when only one other field is unselected", () => {
      const mockConfig: AirbyteStreamConfiguration = {
        ...mockStreamConfiguration,
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE }, { fieldPath: FIELD_TWO }],
      };

      const newStreamConfiguration = updateCursorField(mockConfig, FIELD_ONE, 3);

      expect(newStreamConfiguration).toEqual({
        cursorField: FIELD_ONE,
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE }, { fieldPath: FIELD_TWO }],
      });
    });

    it("updates the cursor field when it is one of many unselected fields", () => {
      const mockConfig: AirbyteStreamConfiguration = {
        ...mockStreamConfiguration,
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE }, { fieldPath: FIELD_TWO }],
      };

      const newStreamConfiguration = updateCursorField(mockConfig, ["new_cursor"], 100);

      expect(newStreamConfiguration).toEqual({
        cursorField: ["new_cursor"],
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE }, { fieldPath: FIELD_TWO }, { fieldPath: ["new_cursor"] }],
      });
    });

    it("disables field selection when the selected cursor is the only unselected field", () => {
      const mockConfig: AirbyteStreamConfiguration = {
        ...mockStreamConfiguration,
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE }, { fieldPath: FIELD_TWO }],
      };

      const newStreamConfiguration = updateCursorField(mockConfig, FIELD_THREE, 3);

      expect(newStreamConfiguration).toEqual({
        cursorField: FIELD_THREE,
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
      primaryKey: [FIELD_ONE],
    };

    const newStreamConfiguration = updatePrimaryKey(mockConfig, [FIELD_TWO], 3);

    expect(newStreamConfiguration).toEqual({
      primaryKey: [FIELD_TWO],
    });
  });

  describe("when fieldSelection is active", () => {
    it("adds each piece of the composite primary key to selectedFields", () => {
      const mockConfig: AirbyteStreamConfiguration = {
        ...mockStreamConfiguration,
        primaryKey: [FIELD_ONE],
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE }],
      };

      const newStreamConfiguration = updatePrimaryKey(mockConfig, [FIELD_TWO, FIELD_THREE], 100);

      expect(newStreamConfiguration).toEqual({
        primaryKey: [FIELD_TWO, FIELD_THREE],
        selectedFields: [{ fieldPath: FIELD_ONE }, { fieldPath: FIELD_TWO }, { fieldPath: FIELD_THREE }],
        fieldSelectionEnabled: true,
      });
    });

    it("replaces the primary key when many other field are unselected", () => {
      const mockConfig: AirbyteStreamConfiguration = {
        ...mockStreamConfiguration,
        primaryKey: [],
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE }, { fieldPath: FIELD_TWO }],
      };

      const newStreamConfiguration = updatePrimaryKey(mockConfig, [FIELD_THREE], 100);

      expect(newStreamConfiguration).toEqual({
        primaryKey: [FIELD_THREE],
        selectedFields: [{ fieldPath: FIELD_ONE }, { fieldPath: FIELD_TWO }, { fieldPath: FIELD_THREE }],
        fieldSelectionEnabled: true,
      });
    });

    it("replaces the primary key when only one other field is unselected", () => {
      const mockConfig: AirbyteStreamConfiguration = {
        ...mockStreamConfiguration,
        primaryKey: [FIELD_ONE],
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE }, { fieldPath: FIELD_TWO }],
      };

      const newStreamConfiguration = updatePrimaryKey(mockConfig, [FIELD_TWO], 3);

      expect(newStreamConfiguration).toEqual({
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE }, { fieldPath: FIELD_TWO }],
        primaryKey: [FIELD_TWO],
      });
    });

    it("disables field selection when the selected primary key is the last unselected field", () => {
      const mockConfig: AirbyteStreamConfiguration = {
        ...mockStreamConfiguration,
        primaryKey: [],
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE }],
      };

      const newStreamConfiguration = updatePrimaryKey(mockConfig, [FIELD_TWO, FIELD_THREE], 3);

      expect(newStreamConfiguration).toEqual({
        primaryKey: [FIELD_TWO, FIELD_THREE],
        selectedFields: [],
        fieldSelectionEnabled: false,
      });
    });

    it("disables field selection when part of the selected primary key is the last unselected field", () => {
      const mockConfig: AirbyteStreamConfiguration = {
        ...mockStreamConfiguration,
        primaryKey: [FIELD_ONE],
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE }, { fieldPath: FIELD_TWO }],
      };

      const newStreamConfiguration = updatePrimaryKey(mockConfig, [FIELD_THREE], 3);

      expect(newStreamConfiguration).toEqual({
        primaryKey: [FIELD_THREE],
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
      primaryKey: [FIELD_ONE],
    };

    const newStreamConfiguration = toggleFieldInPrimaryKey(mockConfig, FIELD_TWO, 3);

    expect(newStreamConfiguration).toEqual({
      primaryKey: [FIELD_ONE, FIELD_TWO],
    });
  });

  describe("when fieldSelection is active", () => {
    it("adds the new primary key field to selectedFields", () => {
      const mockConfig: AirbyteStreamConfiguration = {
        ...mockStreamConfiguration,
        primaryKey: [FIELD_ONE],
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE }, { fieldPath: FIELD_TWO }],
      };

      const newStreamConfiguration = toggleFieldInPrimaryKey(mockConfig, FIELD_THREE, 100);

      expect(newStreamConfiguration).toEqual({
        primaryKey: [FIELD_ONE, FIELD_THREE],
        selectedFields: [{ fieldPath: FIELD_ONE }, { fieldPath: FIELD_TWO }, { fieldPath: FIELD_THREE }],
        fieldSelectionEnabled: true,
      });
    });

    it("adds the new primary key when only one other field is unselected", () => {
      const mockConfig: AirbyteStreamConfiguration = {
        ...mockStreamConfiguration,
        primaryKey: [],
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE }, { fieldPath: FIELD_TWO }],
      };

      const newStreamConfiguration = toggleFieldInPrimaryKey(mockConfig, FIELD_TWO, 3);

      expect(newStreamConfiguration).toEqual({
        primaryKey: [FIELD_TWO],
        selectedFields: [{ fieldPath: FIELD_ONE }, { fieldPath: FIELD_TWO }],
        fieldSelectionEnabled: true,
      });
    });

    it("adds the new primary key when it is one of many unselected fields", () => {
      const mockConfig: AirbyteStreamConfiguration = {
        ...mockStreamConfiguration,
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE }],
      };

      const newStreamConfiguration = toggleFieldInPrimaryKey(mockConfig, FIELD_TWO, 100);

      expect(newStreamConfiguration).toEqual({
        primaryKey: [FIELD_TWO],
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE }, { fieldPath: FIELD_TWO }],
      });
    });

    it("disables field selection when selected primary key is the last unselected field", () => {
      const mockConfig: AirbyteStreamConfiguration = {
        ...mockStreamConfiguration,
        primaryKey: [FIELD_ONE],
        fieldSelectionEnabled: true,
        selectedFields: [{ fieldPath: FIELD_ONE }, { fieldPath: FIELD_TWO }],
      };

      const newStreamConfiguration = toggleFieldInPrimaryKey(mockConfig, FIELD_THREE, 3);

      expect(newStreamConfiguration).toEqual({
        primaryKey: [FIELD_ONE, FIELD_THREE],
        selectedFields: [],
        fieldSelectionEnabled: false,
      });
    });
  });
});
