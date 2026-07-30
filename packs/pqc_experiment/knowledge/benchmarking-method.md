## Measuring PQC honestly

**Discard warm-up.** The first calls into a crypto library pay for lazy
initialisation, table construction and page faults. Run ten or more iterations
before recording anything.

**Report the median and a high percentile.** ML-DSA signing uses rejection
sampling: most attempts succeed on the first try, some need several rounds. The
distribution is right-skewed, so a mean hides the tail that actually determines
worst-case latency. Report median and p95 or p99.

**Interleave when comparing.** Measuring algorithm A to completion and then B
lets thermal state drift between them. Alternate A, B, A, B so both see the
same conditions.

**Pin down what you are timing.** Key generation, encapsulation, decapsulation,
signing and verification have very different costs. Verification is usually
much cheaper than signing for ML-DSA; the reverse of intuition from RSA, where
verification with a small exponent is the cheap side.

**Wire size is len(bytes).** `sys.getsizeof` reports Python object overhead and
will mislead you by dozens of bytes. Serialise and measure the length.

## Phone-specific hazards

Thermal throttling means a long benchmark run reports slower numbers at the end
than at the start. Check by running the sequence forwards and backwards and
comparing. Scheduling noise on a shared little core can dominate a
sub-millisecond operation; if the p99 is more than ten times the median, you are
measuring the scheduler, not the algorithm.

## Known-answer tests

FIPS 203, 204 and 205 ship with test vectors, and the ACVP project publishes
machine-readable versions. A known-answer test checks that a given seed produces
exactly the specified key, ciphertext or signature. It verifies correctness only.
It says nothing about constant-time behaviour, and an implementation can pass
every vector while leaking the secret key through timing.

Deterministic and randomised signing differ: ML-DSA supports both, and vectors
usually specify the deterministic path so results are reproducible.
