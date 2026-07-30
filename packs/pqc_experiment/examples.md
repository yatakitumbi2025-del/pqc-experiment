### Q: Benchmark ML-KEM-768 keygen and encapsulation

Requires `python-oqs`, which needs liboqs built. On Termux:

```bash
pkg install cmake ninja clang python
pip install liboqs-python
```

```python
import statistics
import time

import oqs

ALG = "ML-KEM-768"
N = 200

keygen, encaps, decaps = [], [], []

with oqs.KeyEncapsulation(ALG) as client:
    for i in range(N + 10):
        t0 = time.perf_counter()
        pk = client.generate_keypair()
        t1 = time.perf_counter()

        with oqs.KeyEncapsulation(ALG) as server:
            t2 = time.perf_counter()
            ct, ss_server = server.encap_secret(pk)
            t3 = time.perf_counter()

        t4 = time.perf_counter()
        ss_client = client.decap_secret(ct)
        t5 = time.perf_counter()

        assert ss_client == ss_server, "shared secrets differ"

        if i >= 10:                      # discard warm-up
            keygen.append((t1 - t0) * 1e3)
            encaps.append((t3 - t2) * 1e3)
            decaps.append((t5 - t4) * 1e3)

print(f"{ALG}, {N} iterations, 10 discarded as warm-up")
print(f"public key  {len(pk)} bytes")
print(f"ciphertext  {len(ct)} bytes")
print(f"shared secret {len(ss_client)} bytes")
print()
print(f"{'op':<12}{'median ms':>12}{'p95 ms':>10}")
for name, xs in (("keygen", keygen), ("encapsulate", encaps),
                 ("decapsulate", decaps)):
    xs_sorted = sorted(xs)
    p95 = xs_sorted[int(0.95 * len(xs_sorted))]
    print(f"{name:<12}{statistics.median(xs):>12.3f}{p95:>10.3f}")
```

Method notes: ten warm-up iterations are discarded because the first calls pay
for lazy initialisation. Medians are reported rather than means because phone
CPUs throttle and a single stall would drag the mean. Expect ML-KEM-768 keygen
in the low hundreds of microseconds on a modern ARM core, but treat that as a
prediction to test, not a result.

### Q: Compare handshake byte counts without installing anything

This measures structure, not cryptography — no primitive is executed, so the
numbers are exact rather than estimated.

```python
GROUPS = {
    "X25519":            {"client_share": 32,   "server_share": 32},
    "ML-KEM-768":        {"client_share": 1184, "server_share": 1088},
    "X25519MLKEM768":    {"client_share": 32 + 1184, "server_share": 32 + 1088},
}

print(f"{'group':<18}{'client':>9}{'server':>9}{'total':>9}")
for name, g in GROUPS.items():
    total = g["client_share"] + g["server_share"]
    print(f"{name:<18}{g['client_share']:>9}{g['server_share']:>9}{total:>9}")
```

The hybrid group costs about 2336 bytes of key share against 64 for X25519
alone. That is the number that decides whether a handshake still fits in the
initial congestion window.
