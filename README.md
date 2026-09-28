# Flaky Test Investigator

A small command-line tool for repeatedly executing a test or verification command and measuring whether its behavior is stable.

The project focuses on a frustrating CI problem: a test that is green most of the time can still waste hours if failures are intermittent and the evidence from each run is lost.

The first version will keep the model simple: run one trusted command repeatedly, capture every outcome, and classify the observed behavior without hiding failures behind automatic retries.
