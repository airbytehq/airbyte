# THIS STOPS SOME MODELS TESTS FROM FALLING OVER. IT'S A HACK, WE SHOULD PIN DOWN WHAT'S ACTUALLY GOING ON HERE

# Import the thing that needs to be imported to stop the tests from falling over
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
# "Use" the thing so that the linter doesn't complain
placeholder = ManifestDeclarativeSource
