# THIS STOPS SOME MODELS TESTS FROM FALLING OVER. IT'S A HACK, WE SHOULD PIN DOWN WHAT'S ACTUALLY GOING ON HERE
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
