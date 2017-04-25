# Performance tests for Apache OpenWhisk
A few simple but efficient performance test suites for Apache OpenWhisk. Determines the maximum throughput and end-user latency of the system.

## Test setup
- A standard OpenWhisk system is deployed. Note that the edge nginx router and API Gateway are left out currently. As a consequence, the tests talk directly to the controller.
- Limits are set to 999999 each, for the test's load that means: No throttling at all.
- The deployment uses a docker setup as proposed by the OpenWhisk development team: `overlay` driver and HTTP API enabled via a UNIX port.

The load is driven by the beautiful [`loadtest`](https://www.npmjs.com/package/loadtest) module.

### Travis' machine setup
The [machine provided by Travis](https://docs.travis-ci.com/user/ci-environment/#Virtualization-environments) has ~2 CPU cores (likely shared through virtualization) and 7.5GB memory.

## Suites

### Latency test
The latency test determines the end-to-end latency a user experiences when doing a blocking invocation. The action used is a noop so the numbers returned are plain overhead of the OpenWhisk system.

- 1 HTTP request at a time (concurrency: 1)
- 10.000 samples with a single user
- noop action

**Note:** The throughput number has a 100% correlation with the latency in this case. This test does not serve to determine the maximum throughput of the system.

### Throughput test
The throughput test determines the maximum throughput a user can get out of the system while using a single action. The action used again is a noop, so the numbers are plain OpenWhisk overhead. Note that the throughput does not directly correlate to end-to-end latency here, as the system does more processing in the background as it shows to the user in a blocking invocation.

- 4 HTTP requests at a time (concurrency: 4) (basically CPU cores * 2 to exploit some buffering)
- 10.000 samples with a single user
- noop action

## Running the suites yourself
To run the suites against your own system (or any other OpenWhisk deployment really), simply use the repsective script in `/tests` script. Their parameters are defined inline in the respective file.