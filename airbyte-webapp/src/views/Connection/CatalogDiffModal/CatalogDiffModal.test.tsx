import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { IntlProvider } from "react-intl";

import { CatalogDiff, StreamTransform } from "core/request/AirbyteClient";

import messages from "../../../locales/en.json";
import { CatalogDiffModal } from "./CatalogDiffModal";

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
      { transformType: "add_field", fieldName: ["users", "phone"] },
      { transformType: "add_field", fieldName: ["users", "email"] },
      { transformType: "remove_field", fieldName: ["users", "lastName"] },

      {
        transformType: "update_field_schema",
        fieldName: ["users", "address"],
        updateFieldSchema: { oldSchema: { type: "number" }, newSchema: { type: "string" } },
      },
    ],
  },
];

const mockCatalog = {
  streams: [],
};

describe("catalog diff modal", () => {
  afterEach(cleanup);

  test("it renders the correct section for each type of transform", () => {
    //todo: should this render w the modal service here or not?

    mockCatalogDiff.transforms.push(...addedItems, ...removedItems, ...updatedItems);

    render(
      <IntlProvider messages={messages} locale="en">
        <CatalogDiffModal
          catalogDiff={mockCatalogDiff}
          catalog={mockCatalog}
          onClose={() => {
            return null;
          }}
        />
      </IntlProvider>
    );

    const newStreamsTable = screen.getByRole("table", { name: /new streams/ });
    expect(newStreamsTable).toBeInTheDocument();

    const removedStreamsTable = screen.getByRole("table", { name: /removed streams/ });
    expect(removedStreamsTable).toBeInTheDocument();

    const updatedStreamsSection = screen.getByRole("list", { name: /table with changes/ });
    expect(updatedStreamsSection).toBeInTheDocument();

    mockCatalogDiff.transforms = [];
  });

  test("added fields are not rendered when not in the diff", () => {
    mockCatalogDiff.transforms.push(...removedItems, ...updatedItems);

    render(
      <IntlProvider messages={messages} locale="en">
        <CatalogDiffModal
          catalogDiff={mockCatalogDiff}
          catalog={mockCatalog}
          onClose={() => {
            return null;
          }}
        />
      </IntlProvider>
    );

    const newStreamsTable = screen.queryByRole("table", { name: /new streams/ });
    expect(newStreamsTable).not.toBeInTheDocument();
    mockCatalogDiff.transforms = [];
  });

  test("removed fields are not rendered when not in the diff", () => {
    mockCatalogDiff.transforms.push(...addedItems, ...updatedItems);

    render(
      <IntlProvider messages={messages} locale="en">
        <CatalogDiffModal
          catalogDiff={mockCatalogDiff}
          catalog={mockCatalog}
          onClose={() => {
            return null;
          }}
        />
      </IntlProvider>
    );

    const removedStreamsTable = screen.queryByRole("table", { name: /removed streams/ });
    expect(removedStreamsTable).not.toBeInTheDocument();
    mockCatalogDiff.transforms = [];
  });

  test("changed streams accordion opens/closes on clicking the description row", () => {
    mockCatalogDiff.transforms.push(...addedItems, ...updatedItems);

    render(
      <IntlProvider messages={messages} locale="en">
        <CatalogDiffModal
          catalogDiff={mockCatalogDiff}
          catalog={mockCatalog}
          onClose={() => {
            return null;
          }}
        />
      </IntlProvider>
    );

    const accordionHeader = screen.getByRole("button", { name: /toggle accordion/ });

    expect(accordionHeader).toBeInTheDocument();

    const nullAccordionBody = screen.queryByRole("table", { name: /removed fields/ });
    expect(nullAccordionBody).not.toBeInTheDocument();

    userEvent.click(accordionHeader);
    const openAccordionBody = screen.getByRole("table", { name: /removed fields/ });
    expect(openAccordionBody).toBeInTheDocument();

    userEvent.click(accordionHeader);
    const nullAccordionBodyAgain = screen.queryByRole("table", { name: /removed fields/ });
    expect(nullAccordionBodyAgain).not.toBeInTheDocument();
  });
});
