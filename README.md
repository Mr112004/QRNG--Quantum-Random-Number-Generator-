# QRNG--Quantum-Random-Number-Generator-
Super Quantum generates cryptographically secure keys using true quantum entropy. We replace deterministic PRNGs with physical quantum phenomena, offering a high-performance solution for verifiable, absolute randomness.


This interface can connect to a real quantum backend (IBM / Qiskit or a QRNG API) and use true quantum measurement
results to produce entropy for keys. Telemetry (entropy, bitrate, latency) is exposed via /qrng-stats.

IBM Quantum & Qiskit integration

1. Obtain an IBM API token and configure server-side Qiskit runtime.
2. Submit short circuits (Hadamard -> measure) to collect raw bitstrings.
3. Server computes entropy and bitrate, serves them to the Ul at /qrng-stats.
4. Ul visualizer reacts to telemetry. Show job id metadata for verification.
