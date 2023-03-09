
# airbyte-webapp

This module contains the Airbyte Webapp. It is a React app written in TypeScript. It runs in a Docker container. A very lightweight nginx server runs in that Docker container and serves the webapp.

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.<br />
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

### `npm test`

Launches the test runner in the interactive watch mode.<br />

### `npm run build`

Builds the app for production to the `build` folder.<br />

### VERSION=yourtag ./gradlew :airbyte-webapp:assemble

Builds the app and Docker image and tags the image with `yourtag`.
Note: needs to be run from the root directory of the Airbyte project.

## Entrypoints
* `airbyte-webapp/src/App.tsx` is the entrypoint into the OSS version of the webapp.
* `airbyte-webapp/src/packages/cloud/App.tsx` is the entrypoint into the Cloud version of the webapp.


## Change log:
#### 2023.03.09
1. Sign out change location and add confim popup.
#### 2023.03.08
1. Overall size improvements
#### 2023.03.07
1. Bugfix:Table&page scroll style
#### 2023.03.06
1. New UI content update
2. Bugfix:Table&page scroll style
3. Connection page UI improvements
#### 2023.03.02
1. Error UI
2. Fix the problem that the Tab component on the Source/Destination page is not selected.
3. Cancel left and right sliding fixed style
#### 2023.03.01
1. Supplementary modal styles and adjust some background colors.
#### 2023.02.28
1. Change source/destination/connection ui
#### 2023.02.21
1. Change sidebar settings style as same as other buttons(files:sidebar.tsx)
2. User management page, small screen automatic adaptation problem (files.CustomSelect.tsx)
#### 2023.01.31
1. change wording in Alpha connectors (file: link.ts&en.json&WarningMessage.tsx)
#### 2023.01.13
1. Hide sync log (file: components/JobItem/JobItem.tsx)
2. Change link in connection config (file:links.ts(syncModeLink))
#### 2022.12.29
1. Add copy function for ource/destination page
#### 2022.12.28
1. Show source & destination pages (file: views/layout/sideBar)
#### 2022.12.27
1. Add an edit icon to the connections page (file: EntityTable/ConnectionTable.tsx&EntityTable/components/ConnectionSettingsCell.tsx&Switch/Switch.tsx)
2. Displays notification Settings (file: SettingsPage/SettingsPage.tsx&SettingsPage/pages/NotificationPage/NotificationPage.tsx)
#### 2022.12.14
1. Add sign out button in sidebar (file: en.json&SideBar.tsx)
#### 2022.12.13
1. Airbtyte replaced by Daspire (file: en.json)
2. Hide error log (file: ConnectorCard.tsx)
#### 2022.12.12
1. Add privacy & terms jump link for webapp registration page(file：links.ts&SignupForm.tsx)
