import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { IntlProvider } from "react-intl";

import {
  AirbyteCatalog,
  CatalogDiff,
  DestinationSyncMode,
  StreamTransform,
  SyncMode,
} from "core/request/AirbyteClient";
import { ModalServiceProvider } from "hooks/services/Modal";

import { CatalogDiffModal } from "./CatalogDiffModal";
import messages from "../../../locales/en.json";

const mockCatalogDiff: CatalogDiff = {
  transforms: [],
};

const removedItems: StreamTransform[] = [
  {
    transformType: "remove_stream",
    streamDescriptor: { namespace: "apple", name: "dragonfruit" },
  },
  {
    transformType: "remove_stream",
    streamDescriptor: { namespace: "apple", name: "eclair" },
  },
  {
    transformType: "remove_stream",
    streamDescriptor: { namespace: "apple", name: "fishcake" },
  },
  {
    transformType: "remove_stream",
    streamDescriptor: { namespace: "apple", name: "gelatin_mold" },
  },
];

const addedItems: StreamTransform[] = [
  {
    transformType: "add_stream",
    streamDescriptor: { namespace: "apple", name: "banana" },
  },
  {
    transformType: "add_stream",
    streamDescriptor: { namespace: "apple", name: "carrot" },
  },
];

const updatedItems: StreamTransform[] = [
  {
    transformType: "update_stream",
    streamDescriptor: { namespace: "apple", name: "harissa_paste" },
    updateStream: [
      { transformType: "add_field", fieldName: ["users", "phone"], breaking: false },
      { transformType: "add_field", fieldName: ["users", "email"], breaking: false },
      { transformType: "remove_field", fieldName: ["users", "lastName"], breaking: false },

      {
        transformType: "update_field_schema",
        fieldName: ["users", "address"],
        breaking: false,
        updateFieldSchema: { oldSchema: { type: "number" }, newSchema: { type: "string" } },
      },
    ],
  },
];

const mockCatalog: AirbyteCatalog = {
  streams: [
    {
      stream: {
        namespace: "apple",
        name: "banana",
      },
      config: {
        syncMode: SyncMode.full_refresh,
        destinationSyncMode: DestinationSyncMode.overwrite,
      },
    },
    {
      stream: {
        namespace: "apple",
        name: "carrot",
      },
      config: {
        syncMode: SyncMode.full_refresh,
        destinationSyncMode: DestinationSyncMode.overwrite,
      },
    },
    {
      stream: {
        namespace: "apple",
        name: "dragonfruit",
      },
      config: {
        syncMode: SyncMode.full_refresh,
        destinationSyncMode: DestinationSyncMode.overwrite,
      },
    },
    {
      stream: {
        namespace: "apple",
        name: "eclair",
      },
      config: {
        syncMode: SyncMode.full_refresh,
        destinationSyncMode: DestinationSyncMode.overwrite,
      },
    },
    {
      stream: {
        namespace: "apple",
        name: "fishcake",
      },
      config: {
        syncMode: SyncMode.incremental,
        destinationSyncMode: DestinationSyncMode.append_dedup,
      },
    },
    {
      stream: {
        namespace: "apple",
        name: "gelatin_mold",
      },
      config: {
        syncMode: SyncMode.incremental,
        destinationSyncMode: DestinationSyncMode.append_dedup,
      },
    },
    {
      stream: {
        namespace: "apple",
        name: "harissa_paste",
      },
      config: {
        syncMode: SyncMode.full_refresh,
        destinationSyncMode: DestinationSyncMode.overwrite,
      },
    },
  ],
};

describe("catalog diff modal", () => {
  afterEach(cleanup);
  beforeEach(() => {
    mockCatalogDiff.transforms = [];
  });

  it("renders the correct section for each type of transform", () => {
    mockCatalogDiff.transforms.push(...addedItems, ...removedItems, ...updatedItems);

    render(
      <IntlProvider messages={messages} locale="en">
        <ModalServiceProvider>
          <CatalogDiffModal
            catalogDiff={mockCatalogDiff}
            catalog={mockCatalog}
            onClose={() => {
              return null;
            }}
          />
        </ModalServiceProvider>
      </IntlProvider>
    );

    /**
     * tests for:
     * - proper sections being created
     * - syncmode string is only rendered for removed streams
     */

    const newStreamsTable = screen.getByRole("table", { name: /new streams/ });
    expect(newStreamsTable).toBeInTheDocument();

    const newStreamRow = screen.getByRole("row", { name: "apple banana" });
    expect(newStreamRow).toBeInTheDocument();

    const newStreamRowWithSyncMode = screen.queryByRole("row", { name: "apple carrot incremental | append_dedup" });
    expect(newStreamRowWithSyncMode).not.toBeInTheDocument();

    const removedStreamsTable = screen.getByRole("table", { name: /removed streams/ });
    expect(removedStreamsTable).toBeInTheDocument();

    const removedStreamRowWithSyncMode = screen.getByRole("row", {
      name: "apple dragonfruit full_refresh | overwrite",
    });
    expect(removedStreamRowWithSyncMode).toBeInTheDocument();

    const updatedStreamsSection = screen.getByRole("list", { name: /table with changes/ });
    expect(updatedStreamsSection).toBeInTheDocument();

    const updatedStreamRowWithSyncMode = screen.queryByRole("row", {
      name: "apple harissa_paste full_refresh | overwrite",
    });
    expect(updatedStreamRowWithSyncMode).not.toBeInTheDocument();
  });

  it("added fields are not rendered when not in the diff", () => {
    mockCatalogDiff.transforms.push(...removedItems, ...updatedItems);

    render(
      <IntlProvider messages={messages} locale="en">
        <ModalServiceProvider>
          <CatalogDiffModal
            catalogDiff={mockCatalogDiff}
            catalog={mockCatalog}
            onClose={() => {
              return null;
            }}
          />
        </ModalServiceProvider>
      </IntlProvider>
    );

    const newStreamsTable = screen.queryByRole("table", { name: /new streams/ });
    expect(newStreamsTable).not.toBeInTheDocument();
  });

  it("removed fields are not rendered when not in the diff", () => {
    mockCatalogDiff.transforms.push(...addedItems, ...updatedItems);

    render(
      <IntlProvider messages={messages} locale="en">
        <ModalServiceProvider>
          <CatalogDiffModal
            catalogDiff={mockCatalogDiff}
            catalog={mockCatalog}
            onClose={() => {
              return null;
            }}
          />
        </ModalServiceProvider>
      </IntlProvider>
    );

    const removedStreamsTable = screen.queryByRole("table", { name: /removed streams/ });
    expect(removedStreamsTable).not.toBeInTheDocument();
  });

  it("changed streams accordion opens/closes on clicking the description row", () => {
    mockCatalogDiff.transforms.push(...addedItems, ...updatedItems);

    render(
      <IntlProvider messages={messages} locale="en">
        <ModalServiceProvider>
          <CatalogDiffModal
            catalogDiff={mockCatalogDiff}
            catalog={mockCatalog}
            onClose={() => {
              return null;
            }}
          />
        </ModalServiceProvider>
      </IntlProvider>
    );

    const accordionHeader = screen.getByTestId(`toggle-accordion-harissa_paste-stream`);

    expect(accordionHeader).toBeInTheDocument();

    const nullAccordionBody = screen.queryByRole("table", { name: /removed fields/ });
    expect(nullAccordionBody).not.toBeInTheDocument();

    userEvent.click(accordionHeader);
    const openAccordionBody = screen.getByRole("table", { name: /removed fields/ });
    expect(openAccordionBody).toBeInTheDocument();

    userEvent.click(accordionHeader);
    const nullAccordionBodyAgain = screen.queryByRole("table", { name: /removed fields/ });
    expect(nullAccordionBodyAgain).not.toBeInTheDocument();
    mockCatalogDiff.transforms = [];
  });
});
