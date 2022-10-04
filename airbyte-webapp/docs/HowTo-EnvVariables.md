## Environment variables

Currently we have 2 types of environment variables:

1. Statically injected build time variables
2. Dynamic env variables injected via `window`

### Static env variables

The environment variables are embedded during the build time. Since our app is based on Create React App that produces a
static HTML/CSS/JS bundle, it can’t possibly read them at runtime.

Static env variables name should always start with `REACT_APP_`

### Dynamic env variables

Dynamic env variables in our cases are injected into app by nginx

```html
<script language="javascript" \>
  window.TRACKING_STRATEGY = "$TRACKING_STRATEGY";
  window.AIRBYTE_VERSION = "$AIRBYTE_VERSION";
  window.API_URL = "$API_URL";
</script>
;
```

later we can use any of the declared variables from window
