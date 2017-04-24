# Performance tests for Apache OpenWhisk
A few simple but efficient performance test suites for Apache OpenWhisk. Determines the maximum throughput and end-user latency of the system.

## Test setup
- A standard OpenWhisk system is deployed. Note that the edge nginx router and API Gateway are left out currently.
- Limits are set to 999999 each, for the test's load that means: No throttling at all.
- The deployment uses a docker setup as proposed by the OpenWhisk development team: `overlay` driver and HTTP API enabled via a UNIX port.

### Travis' machine setup
The [machine provided by Travis](https://docs.travis-ci.com/user/ci-environment/#Virtualization-environments) has ~2 CPU cores (likely shared through virtualization) and 7.5GB memory.

## Latency test
The latency test determines the end-to-end latency a user experiences when doing a blocking invocation. The action used is a noop so the numbers returned are plain overhead of the OpenWhisk system.

- 1 HTTP request at a time (concurrency: 1)
- 10.000 samples with a single user
- noop action
