# Google Analytics Source

## Documentation
* [User Documentation](https://docs.airbyte.io/integrations/sources/googleanalytics)

## For Airbyte employees
To send test traffic for this test, you can send page view data with:
```
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-158543392-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'UA-158543392-1');
</script>
```

TODO: Send this data with a bot automatically as part of the test 
