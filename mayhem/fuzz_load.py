#!/usr/bin/env python3
"""Atheris fuzz harness for python-bibtexparser (v1 API, this commit's era).

Ported 1:1 from the mayhemheroes fork's original `mayhem/fuzz_load.py` (fork commit
4720c8890acbe1ae8ae09e275cdacf62c45ca8fd): same `EnhancedFuzzedDataProvider` input framing
(`ConsumeBool` picks the `loads`-from-string vs. `load`-from-file branch, then the remainder
is consumed as the string/file payload) and no exception handling — replaying the original
run's crashers byte-for-byte requires the exact same consumption order, or the same bytes
decode into different content and the crash does not reproduce.

At this upstream commit (pre-v2-rewrite) the public entrypoints are the v1
`bibtexparser.loads`/`load`/`dumps`/`dump`, not the later `parse_string`/`write_string`.

Run modes (driven by the compiled launcher `bibtexparser_fuzzer` / `-standalone`):
  * fuzzing      — `python3 fuzz_load.py [libFuzzer args]`
  * single input — `python3 fuzz_load.py <file>` (libFuzzer runs it once)

No harness-side timer: a slow or looping input is a finding, bounded by the runner
(libFuzzer's `-timeout` / Mayhem's per-test timeout), not swallowed here.
"""
import sys

import atheris
import fuzz_helpers

# Instrument the library under test so the fuzzer gets coverage feedback.
with atheris.instrument_imports(include=["bibtexparser"]):
    import bibtexparser


def TestOneInput(data):
    fdp = fuzz_helpers.EnhancedFuzzedDataProvider(data)
    if fdp.ConsumeBool():
        bibtexparser.loads(fdp.ConsumeRemainingString())
    else:
        with fdp.ConsumeMemoryFile(all_data=True, as_bytes=False) as f:
            bibtexparser.load(f)


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
