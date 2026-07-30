## Libraries worth benchmarking

**liboqs** (Open Quantum Safe) is the standard research implementation covering
essentially every candidate, with `liboqs-python` bindings. Best coverage,
explicitly not intended as production-grade.

**PQClean** provides clean, portable reference and optimised implementations
that other projects vendor from. Useful when you want to compile one algorithm
without pulling in a whole framework.

**OpenSSL 3.5 and later** ships ML-KEM, ML-DSA and SLH-DSA in the default
provider, which makes `openssl speed` a quick way to get numbers without
writing any code.

**BoringSSL and Go's crypto libraries** carry the hybrid TLS groups used in
production browser deployments, and are the right reference for what real
handshakes actually negotiate.

## Getting liboqs onto Termux

```bash
pkg install cmake ninja clang git python
pip install liboqs-python
```

The Python package will attempt to build liboqs on first import if it cannot
find a system copy. It is a long build on a phone. If it fails, fall back to
structural measurements — byte counts, serialisation overhead, protocol
framing — which need no native code and are exact.

## What cannot be measured from Python

Constant-time behaviour, cache-timing leakage and power side channels are
invisible to a Python timing loop. Interpreter overhead swamps the signal, and
the operations of interest are inside the native library anyway. Treat these as
out of scope and say so rather than producing a number that looks like an
answer.

## liboqs mechanism names

liboqs takes a parameter set, never a bare family name. `oqs.Signature("ML-DSA")`
raises; the algorithm does not exist under that name.

Signatures: ML-DSA-44, ML-DSA-65, ML-DSA-87. Older builds use Dilithium2,
Dilithium3, Dilithium5. Hash-based: SPHINCS+-SHA2-128s-simple.

KEMs: ML-KEM-512, ML-KEM-768, ML-KEM-1024. Older builds use Kyber512,
Kyber768, Kyber1024.

Check what a build actually supports before writing a benchmark:
`python -c "import oqs; print(oqs.get_enabled_sig_mechanisms())"`
