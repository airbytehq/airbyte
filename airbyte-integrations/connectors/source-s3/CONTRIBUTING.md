# Connector Contributing Guide

The following guide is intended for contributors to the S3 Source Connector. It provides information on how to contribute to the project, including how to set up your development environment, run tests, and submit changes.

Note: Most instructiongs and examples use VS Code. You are free to use another IDE.

## Getting Started

1. If you have not already, clone the `airbyte` repo locally.
2. Open the `airbyte` repo in VS Code.
3. In VS Code, select `File` > `Add Folder to Workspace` and add the `source-s3` folder. This will create a second folder mount directly to the `source-s3` folder. This also enabled test discovery from the `source-s3` folder.
4. Right-click on the `source-s3` folder in the VS Code file explorer and select `Open in Terminal`. This will open a terminal window with the current directory set to the `source-s3` folder.
5. Run `poetry install` to install the project dependencies and create a new virtual environment.
6. In VS Code, select `Python: Select Interpreter` from the status bar and select the virtual environment created by Poetry.
7. In VS Code, navigate to the `Tests` pane in the left-hand sidebar and check that tests are correctly discovered. If not, try clicking the `Refresh Tests` button.
8. If everything is running correctly, you should be able to execute tests directly from within the Test pane UI.
   - Note: You may see a `pytest Discovery Error [airbyte]` message in the test explorer. This is expected, as VS Code tries and fails to detect tests for the monorepo (root) directory. This does not affect the ability to run tests for the `source-s3` directory.
9. Once you have everything working, we recommend saving your workspace configuration under the name `airbyte-source-s3` in the parent folder _above_ the root of the repo. You can do this by selecting `File` > `Save Workspace As...` and saving the workspace file to the parent folder where you cloned the `airbyte` repo. This will allow you to easily open the workspace in the future.
