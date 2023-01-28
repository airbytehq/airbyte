import type { StorybookConfig } from "@storybook/react-vite";

const config: StorybookConfig = {
  framework: "@storybook/react-vite",
  stories: ["../src/**/*.stories.@(ts|tsx)"],
  addons: [
    "@storybook/addon-links",
    "@storybook/addon-essentials",
    "storybook-addon-mock/register",
  ],
  // staticDirs: ["../public"],
  // webpackFinal: config => {
  //   config.resolve.modules.push(process.cwd() + "/node_modules");
  //   config.resolve.modules.push(process.cwd() + "/src");

  //   // this is needed for working w/ linked folders
  //   config.resolve.symlinks = false;
  //   return config;
  // },
};

export default config;