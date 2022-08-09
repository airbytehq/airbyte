import { render, screen } from "@testing-library/react";
import { IntlProvider } from "react-intl";

import { CatalogDiff } from "core/request/AirbyteClient";

import messages from "../../../locales/en.json";
import { CatalogDiffModal } from "./CatalogDiffModal";

const mockCatalogDiff: CatalogDiff = {
  transforms: [
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
    // {
    //   transformType: "update_stream",
    //   streamDescriptor: { namespace: "apple", name: "harissa_paste" },
    //   updateStream: [
    //     { transformType: "add_field", fieldName: ["users", "phone"] },
    //     { transformType: "add_field", fieldName: ["users", "email"] },
    //     { transformType: "remove_field", fieldName: ["users", "lastName"] },

    //     {
    //       transformType: "update_field_schema",
    //       fieldName: ["users", "address"],
    //       updateFieldSchema: { oldSchema: { type: "number" }, newSchema: { type: "string" } },
    //     },
    //   ],
    // },
    {
      transformType: "add_stream",
      streamDescriptor: { namespace: "apple", name: "banana" },
    },
    {
      transformType: "add_stream",
      streamDescriptor: { namespace: "apple", name: "carrot" },
    },
  ],
};

const mockCatalog = {
  streams: [],
};

test("it renders the correct section for added streams", () => {
  //todo: should this render w the modal service here or not?
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
});
test("it renders the correct section for removed streams", () => {});
test("it renders the correct section for changed streams", () => {});
test("changed streams accordion displays correct information", () => {});
test("changed streams accordion opens/closes on clicking the description row", () => {});
