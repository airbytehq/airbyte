import ServiceForm from "components/ServiceForm";
import { render } from "utils/testutils";
import { JSONSchema7 } from "json-schema";

const schema: JSONSchema7 = {
  type: "object",
  required: ["host", "port", "dbname"],
  properties: {
    host: {
      type: "string",
      description: "Hostname of the database.",
      title: "Host",
    },
    port: {
      title: "Port",
      type: "integer",
      description: "Port of the database.",
    },
    password: {
      title: "Password",
      airbyte_secret: true,
      type: "string",
      description: "Password associated with the username.",
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any, // Because airbyte_secret is not part of json_schema
    credentials: {
      type: "object",
      oneOf: [
        {
          title: "api key",
          required: ["api_key"],
          properties: {
            api_key: {
              type: "string",
            },
          },
        },
        {
          title: "oauth",
          required: ["redirect_uri"],
          properties: {
            redirect_uri: {
              type: "string",
              examples: ["https://api.hubspot.com/"],
            },
          },
        },
      ],
    },
    message: {
      type: "string",
      multiline: true,
      title: "Message",
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any, // Because multiline is not part of json_schema
    priceList: {
      type: "array",
      items: {
        type: "object",
        properties: {
          name: {
            type: "string",
            title: "Product name",
          },
          price: {
            type: "integer",
            title: "Price ($)",
          },
        },
      },
    },
    emails: {
      type: "array",
      items: {
        type: "string",
      },
    },
    workTime: {
      type: "array",
      title: "Work time",
      items: {
        type: "string",
        enum: ["day", "night"],
      },
    },
  },
};

test("should display complex json schema specs", async () => {
  const { container } = render(
    <ServiceForm
      formType="source"
      onSubmit={() => null}
      specifications={schema}
      dropDownData={[]}
    />
  );

  const name = container.querySelector("input[name='name']");
  const serviceType = container.querySelector(
    "div[data-test-id='serviceType']"
  );

  const host = container.querySelector(
    "input[name='connectionConfiguration.host']"
  );
  const port = container.querySelector(
    "input[name='connectionConfiguration.port']"
  );
  const password = container.querySelector(
    "input[name='connectionConfiguration.password']"
  );
  const credentials = container.querySelector(
    "div[data-test-id='connectionConfiguration.credentials']"
  );
  const credentialsValue = credentials?.querySelector("input[value='api key']");
  const apiKey = container.querySelector(
    "input[name='connectionConfiguration.credentials.api_key']"
  );
  const message = container.querySelector(
    "textarea[name='connectionConfiguration.message']"
  );
  const emails = container.querySelector(
    "input[name='connectionConfiguration.emails']"
  );
  const workTime = container.querySelector(
    "div[name='connectionConfiguration.workTime']"
  );
  const priceList = container.querySelector(
    "div[data-test-id='connectionConfiguration.priceList']"
  );
  const addButton = priceList?.querySelector(
    "button[data-test-id='addItemButton']"
  );

  expect(name).toBeInTheDocument();
  expect(serviceType).toBeInTheDocument();

  expect(host).toBeInTheDocument();
  expect(host?.getAttribute("type")).toEqual("text");

  expect(port).toBeInTheDocument();
  expect(port?.getAttribute("type")).toEqual("number");

  expect(password).toBeInTheDocument();
  expect(password?.getAttribute("type")).toEqual("password");

  expect(credentials).toBeInTheDocument();
  expect(credentials?.getAttribute("role")).toEqual("combobox");
  expect(credentialsValue).toBeInTheDocument();

  expect(apiKey).toBeInTheDocument();

  expect(message).toBeInTheDocument();

  expect(emails).toBeInTheDocument();

  expect(workTime).toBeInTheDocument();

  expect(priceList).toBeInTheDocument();
  expect(addButton).toBeInTheDocument();
});
