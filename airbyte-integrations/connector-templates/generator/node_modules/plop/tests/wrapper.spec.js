import fs from "node:fs";
import { resolve, dirname } from "node:path";
import { waitFor } from "cli-testing-library";
import { renderScript } from "./render.js";
import { getFileHelper } from "./file-helper.js";
const { getFilePath } = getFileHelper();
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));

const renderWrapper = (...props) => {
  return renderScript(
    resolve(__dirname, "./examples/wrap-plop/index.js"),
    ...props
  );
};

test("wrapper should show version on v flag", async () => {
  const { findByText } = await renderWrapper(["-v"]);

  expect(await findByText(/^[\w\.-]+$/)).toBeInTheConsole();
});

test("wrapper should prompts", async () => {
  const { findByText, fireEvent } = await renderWrapper([""], {
    cwd: resolve(__dirname, "./examples/wrap-plop"),
  });

  expect(await findByText("What is your name?")).toBeInTheConsole();
});

test("wrapper should bypass prompts with index", async () => {
  const { findByText, queryByText, fireEvent } = await renderWrapper(
    ["Corbin"],
    {
      cwd: resolve(__dirname, "./examples/wrap-plop"),
    }
  );

  expect(await queryByText("What is your name?")).not.toBeInTheConsole();
  expect(
    await findByText("What pizza toppings do you like?")
  ).toBeInTheConsole();
});

test("wrapper should bypass prompts with name", async () => {
  const { findByText, queryByText, fireEvent } = await renderWrapper(
    ["--name", "Corbin"],
    {
      cwd: resolve(__dirname, "./examples/wrap-plop"),
    }
  );

  expect(await queryByText("What is your name?")).not.toBeInTheConsole();
  expect(
    await findByText("What pizza toppings do you like?")
  ).toBeInTheConsole();
});

test("can run actions (add)", async () => {
  const expectedFilePath = await getFilePath(
    "./examples/wrap-plop/output/added.txt"
  );

  const { fireEvent } = await renderWrapper(["Test", "Cheese"], {
    cwd: resolve(__dirname, "./examples/wrap-plop"),
  });

  await waitFor(() => fs.promises.stat(expectedFilePath));

  const data = fs.readFileSync(expectedFilePath, "utf8");

  expect(data).toMatch(/Hello/);
});
