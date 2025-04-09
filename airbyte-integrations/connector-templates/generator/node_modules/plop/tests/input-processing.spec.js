import { resolve, dirname } from "node:path";
import { renderPlop } from "./render.js";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));

test("should report a missing plopfile when not copied", async () => {
  const { findByError } = await renderPlop();
  expect(await findByError(/\[PLOP\] No plopfile found/)).toBeInTheConsole();
});

test("should show help information on help flag", async () => {
  const { findByText } = await renderPlop(["--help"]);
  const { stdoutArr } = await findByText("Usage:");
  expect(stdoutArr.join("\n")).toMatchSnapshot();
});

test("should show version on version flag", async () => {
  const { findByText } = await renderPlop(["--version"]);
  expect(await findByText(/^[\w\.-]+$/)).toBeInTheConsole();
});

test("should show version on v flag", async () => {
  const { findByText } = await renderPlop(["-v"]);
  expect(await findByText(/^[\w\.-]+$/)).toBeInTheConsole();
});

test("should display inquirer prompts", async () => {
  const { findByText, userEvent } = await renderPlop([], {
    cwd: resolve(__dirname, "./examples/prompt-only"),
  });
  expect(await findByText("What is your name?")).toBeInTheConsole();
  userEvent.keyboard("Joe");
  expect(await findByText("Joe")).toBeInTheConsole();
  userEvent.keyboard("[Enter]");
});

test("Should handle generator prompt", async () => {
  const { findByText, clear, userEvent } = await renderPlop([""], {
    cwd: resolve(__dirname, "./examples/javascript"),
  });

  await findByText("Please choose a generator");

  clear();
  userEvent.keyboard("[ArrowUp]");
  userEvent.keyboard("[ArrowDown]");
  userEvent.keyboard("[Enter]");

  expect(await findByText("this is a test")).toBeInTheConsole();
});

test("Should bypass generator prompt", async () => {
  const { findByText } = await renderPlop(["test"], {
    cwd: resolve(__dirname, "./examples/javascript"),
  });

  expect(await findByText("What is your name?")).toBeInTheConsole();
});

test("Should bypass prompt by input", async () => {
  const { queryByText, findByText } = await renderPlop(["Frank"], {
    cwd: resolve(__dirname, "./examples/prompt-only"),
  });

  expect(await queryByText("What is your name?")).not.toBeInTheConsole();
  expect(
    await findByText("What pizza toppings do you like?")
  ).toBeInTheConsole();
});

test("Should bypass prompt by input placeholder", async () => {
  const { queryByText, findByText, userEvent } = await renderPlop(
    ["_", "Cheese"],
    {
      cwd: resolve(__dirname, "./examples/prompt-only"),
    }
  );

  expect(await findByText("What is your name?")).toBeInTheConsole();
  userEvent.keyboard("[Enter]");
  expect(
    await queryByText("What pizza toppings do you like?")
  ).not.toBeInTheConsole();
});

test("Should bypass prompt by name", async () => {
  const { queryByText, findByText } = await renderPlop(
    ["--", "--name", "Frank"],
    {
      cwd: resolve(__dirname, "./examples/prompt-only"),
    }
  );

  expect(await queryByText("What is your name?")).not.toBeInTheConsole();
  expect(
    await findByText("What pizza toppings do you like?")
  ).toBeInTheConsole();
});

test("Should allow for empty string bypassing", async () => {
  const { queryByText, findByText } = await renderPlop(["--", "--name", `""`], {
    cwd: resolve(__dirname, "./examples/prompt-only"),
  });

  expect(await queryByText("What is your name?")).not.toBeInTheConsole();
  expect(
    await findByText("What pizza toppings do you like?")
  ).toBeInTheConsole();
});

test.todo("Dynamic actions");
