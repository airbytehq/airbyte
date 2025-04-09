import { resolve, dirname } from "node:path";
import { waitFor } from "cli-testing-library";
import * as fs from "node:fs";
import { renderPlop } from "./render.js";
import { getFileHelper } from "./file-helper.js";
const { getFilePath } = getFileHelper();
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));

test("Plop to add and rename files", async () => {
  const expectedFilePath = await getFilePath(
    "./examples/add-action/output/new-output.txt"
  );

  const { findByText, userEvent } = await renderPlop(["addAndNameFile"], {
    cwd: resolve(__dirname, "./examples/add-action"),
  });

  expect(await findByText("What should the file name be?")).toBeInTheConsole();

  userEvent.keyboard("new-output");
  userEvent.keyboard("[Enter]");

  await waitFor(() => fs.promises.stat(expectedFilePath));

  const data = fs.readFileSync(expectedFilePath, "utf8");

  expect(data).toMatch(/Hello/);
});

test("Plop to add and change file contents", async () => {
  const expectedFilePath = await getFilePath(
    "./examples/add-action/output/new-output.txt"
  );

  const { findByText, userEvent } = await renderPlop(["addAndChangeFile"], {
    cwd: resolve(__dirname, "./examples/add-action"),
  });

  expect(await findByText("What's your name?")).toBeInTheConsole();

  userEvent.keyboard("Corbin");
  userEvent.keyboard("[Enter]");

  await waitFor(() => fs.promises.stat(expectedFilePath));

  const data = await fs.promises.readFile(expectedFilePath, "utf8");

  expect(data).toMatch(/Hi Corbin!/);
});

test.todo("Test modify");
test.todo("Test append");
test.todo("Test built-in helpers");
test.todo("Test custom helpers");
