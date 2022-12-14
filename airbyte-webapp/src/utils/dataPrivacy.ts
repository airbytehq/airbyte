declare global {
  interface Window {
    Osano?: {
      cm: {
        mode: "production" | "debug";
        showDrawer: (type: string) => void;
        addEventListener: (event: string, callback: (event: unknown) => void) => void;
      };
    };
  }
}

const GDPR_TIMEZONES = [
  "Africa/Ceuta",
  "Asia/Famagusta",
  "Asia/Nicosia",
  "Atlantic/Azores",
  "Atlantic/Canary",
  "Atlantic/Madeira",
  "Europe/Amsterdam",
  "Europe/Athens",
  "Europe/Berlin",
  "Europe/Bratislava",
  "Europe/Brussels",
  "Europe/Bucharest",
  "Europe/Budapest",
  "Europe/Busingen",
  "Europe/Copenhagen",
  "Europe/Dublin",
  "Europe/Helsinki",
  "Europe/Lisbon",
  "Europe/Ljubljana",
  "Europe/Luxembourg",
  "Europe/Madrid",
  "Europe/Malta",
  "Europe/Paris",
  "Europe/Prague",
  "Europe/Riga",
  "Europe/Rome",
  "Europe/Sofia",
  "Europe/Stockholm",
  "Europe/Tallinn",
  "Europe/Vienna",
  "Europe/Vilnius",
  "Europe/Warsaw",
  "Europe/Zagreb",
];

export const isGdprCountry = (): boolean => {
  const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  return GDPR_TIMEZONES.includes(timeZone);
};

export const loadOsano = (): void => {
  if (!process.env.REACT_APP_OSANO) {
    return;
  }

  // Create style element to hide osano widget
  const style = document.createElement("style");
  style.appendChild(
    document.createTextNode(`
    .osano-cm-widget { display: none; }
    .osano-cm-dialog__close { display: none; }
    .osano-cm-button--type_denyAll { display: none; }
    .osano-cm-button--type_manage { background-color: inherit;  border: 1px #1a194d solid; color: #1a194d; font-weight: 200; }`)
  );
  document.head.appendChild(style);

  // Create and append the script tag to  load osano
  const script = document.createElement("script");
  script.src = `https://cmp.osano.com/${process.env.REACT_APP_OSANO}/osano.js`;
  script.addEventListener("load", () => {
    window.Osano?.cm.addEventListener("osano-cm-script-blocked", (item) => {
      console.debug(`Script blocked by Osano: ${item}`);
    });
    window.Osano?.cm.addEventListener("osano-cm-cookie-blocked", (item) => {
      console.debug(`Cookie blocked by Osano: ${item}`);
    });
  });
  document.head.appendChild(script);
};

export const isOsanoActive = (): boolean => {
  return window.Osano?.cm.mode === "production";
};

export const showOsanoDrawer = (): void => {
  window.Osano?.cm.showDrawer("osano-cm-dom-info-dialog-open");
};
