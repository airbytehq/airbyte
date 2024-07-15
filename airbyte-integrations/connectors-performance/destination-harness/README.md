# destination-harness

Performance harness for destination connectors.

This component is used by the `/connector-performance` GitHub action and is used in order to test throughput of
destination connectors on a number of datasets.

Associated files are:

<li>Main.java - the main entrypoint for the harness
<li>PerformanceTest.java - sets up the destination connector, sends records to it, and measures throughput
<li>run-harness-process.yaml - kubernetes file that processes dynamic arguments and runs the harness
