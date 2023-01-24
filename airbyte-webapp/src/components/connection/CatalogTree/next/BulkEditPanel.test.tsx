import { render } from "@testing-library/react";
import ReactDOM from "react-dom";
import { IntlProvider } from "react-intl";

import { SyncSchemaField, SyncSchemaStream } from "core/domain/catalog";
import en from "locales/en.json";

import { BulkEditPanel, calculateSharedFields, getAvailableSyncModesOptions } from "./BulkEditPanel";
import { SyncModeOption } from "./SyncModeSelect";

const MOCK_NODE_1: SyncSchemaStream = {
  stream: {
    name: "balance_transactions",
    jsonSchema: {
      type: ["null", "object"],
      properties: {
        id: {
          type: ["null", "string"],
        },
        fee: {
          type: ["null", "integer"],
        },
        net: {
          type: ["null", "integer"],
        },
        type: {
          type: ["null", "string"],
        },
        amount: {
          type: ["null", "integer"],
        },
        object: {
          type: ["null", "string"],
        },
        source: {
          type: ["null", "string"],
        },
        status: {
          type: ["null", "string"],
        },
        created: {
          type: ["null", "integer"],
        },
        currency: {
          type: ["null", "string"],
        },
        description: {
          type: ["null", "string"],
        },
        fee_details: {
          type: ["null", "array"],
          items: {
            type: ["null", "object"],
            properties: {
              type: {
                type: ["null", "string"],
              },
              amount: {
                type: ["null", "integer"],
              },
              currency: {
                type: ["null", "string"],
              },
              application: {
                type: ["null", "string"],
              },
              description: {
                type: ["null", "string"],
              },
            },
          },
        },
        available_on: {
          type: ["null", "integer"],
        },
        exchange_rate: {
          type: ["null", "number"],
        },
        sourced_transfers: {
          type: ["null", "array"],
          items: {},
        },
      },
    },
    supportedSyncModes: ["full_refresh", "incremental"],
    sourceDefinedCursor: true,
    defaultCursorField: ["created"],
    sourceDefinedPrimaryKey: [["id"]],
  },
  config: {
    syncMode: "incremental",
    cursorField: ["created"],
    destinationSyncMode: "append_dedup",
    primaryKey: [["id"]],
    aliasName: "balance_transactions",
    selected: true,
  },
  id: "0",
};
const MOCK_NODE_2: SyncSchemaStream = {
  stream: {
    name: "bank_accounts",
    jsonSchema: {
      type: ["null", "object"],
      properties: {
        id: {
          type: ["null", "string"],
        },
        last4: {
          type: ["null", "string"],
        },
        object: {
          type: ["null", "string"],
        },
        status: {
          type: ["null", "string"],
        },
        country: {
          type: ["null", "string"],
        },
        currency: {
          type: ["null", "string"],
        },
        customer: {
          type: ["null", "string"],
        },
        metadata: {
          type: ["null", "object"],
          properties: {},
        },
        bank_name: {
          type: ["null", "string"],
        },
        fingerprint: {
          type: ["null", "string"],
        },
        routing_number: {
          type: ["null", "string"],
        },
        account_holder_name: {
          type: ["null", "string"],
        },
        account_holder_type: {
          type: ["null", "string"],
        },
      },
    },
    supportedSyncModes: ["full_refresh"],
    defaultCursorField: [],
    sourceDefinedPrimaryKey: [["id"]],
  },
  config: {
    syncMode: "full_refresh",
    cursorField: [],
    destinationSyncMode: "overwrite",
    primaryKey: [["id"]],
    aliasName: "bank_accounts",
    selected: true,
  },
  id: "1",
};

jest.mock("hooks/services/BulkEdit/BulkEditService", () => ({
  useBulkEditService: () => ({
    selectedBatchNodes: [MOCK_NODE_1, MOCK_NODE_2],
    options: {
      selected: false,
    },
    isActive: true,
    onChangeOption: jest.fn(),
    onApply: jest.fn(),
    onCancel: jest.fn(),
  }),
}));

jest.mock("hooks/services/ConnectionForm/ConnectionFormService", () => ({
  useConnectionFormService: () => ({ destDefinitionSpecification: ["overwrite", "append", "append_dedup"] }),
}));

const renderBulkEditPanel = () =>
  render(
    <IntlProvider locale="en" messages={en}>
      <BulkEditPanel />
    </IntlProvider>
  );

describe("<BulkEditPanel />", () => {
  beforeAll(() => {
    // @ts-expect-error Okay for test
    ReactDOM.createPortal = (element) => {
      return element;
    };
  });

  it("should render", () => {
    const component = renderBulkEditPanel();
    expect(component).toMatchSnapshot();
  });

  it("calculateSharedFields should work correctly", () => {
    const expectedResult: SyncSchemaField[] = [
      { cleanedName: "id", path: ["id"], key: "id", type: "string" },
      { cleanedName: "object", path: ["object"], key: "object", type: "string" },
      { cleanedName: "status", path: ["status"], key: "status", type: "string" },
      { cleanedName: "currency", path: ["currency"], key: "currency", type: "string" },
    ];
    const actualResult = calculateSharedFields([MOCK_NODE_1, MOCK_NODE_2]);
    expect(actualResult).toEqual(expectedResult);
  });

  it("getAvailableSyncModesOptions should work correctly", () => {
    const expectedResult: SyncModeOption[] = [
      { value: { syncMode: "incremental", destinationSyncMode: "append_dedup" } },
      { value: { syncMode: "full_refresh", destinationSyncMode: "overwrite" } },
      { value: { syncMode: "incremental", destinationSyncMode: "append" } },
      { value: { syncMode: "full_refresh", destinationSyncMode: "append" } },
    ];
    const actualResult = getAvailableSyncModesOptions(
      [MOCK_NODE_1, MOCK_NODE_2],
      ["overwrite", "append", "append_dedup"]
    );
    expect(actualResult).toEqual(expectedResult);
  });
});
