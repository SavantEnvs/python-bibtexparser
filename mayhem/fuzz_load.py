#!/usr/bin/env python3
"""Atheris fuzz harness for python-bibtexparser (v2 API).

Exercises the BibTeX parser (`bibtexparser.parse_string`) on arbitrary input
and, when a Library was produced, round-trips it through the writer
(`bibtexparser.write_string`). Atheris instruments the imported bibtexparser
modules (splitter, model, middlewares, writer), so libFuzzer drives the parser
toward new code paths with coverage feedback.

Historical note: this harness keeps the original `loader-fuzz` target name.
The original harness fuzzed the v1 API (`bibtexparser.loads`/`load`); upstream's
default branch is now the v2 rewrite, so the same code path (string -> parsed
library) is exercised through the v2 entrypoints.

Run modes (driven by the compiled launcher `bibtexparser_fuzzer` / `-standalone`):
  * fuzzing      — `python3 fuzz_load.py [libFuzzer args]`
  * single input — `python3 fuzz_load.py <file>` (libFuzzer runs it once)

No harness-side timer: a slow or looping input is a finding, bounded by the runner
(libFuzzer's `-timeout` / Mayhem's per-test timeout), not swallowed here.
"""
import sys

import atheris

# Instrument the library under test so the fuzzer gets coverage feedback.
with atheris.instrument_imports(include=["bibtexparser"]):
    import bibtexparser


@atheris.instrument_func
def TestOneInput(data):
    fdp = atheris.FuzzedDataProvider(data)
    text = fdp.ConsumeUnicodeNoSurrogates(fdp.remaining_bytes())
    try:
        library = bibtexparser.parse_string(text)
        # Round-trip through the writer (forces model/writer code paths).
        bibtexparser.write_string(library)
    except bibtexparser.exceptions.ParsingException:
        # Library-defined parse errors are the expected outcome for bad input.
        pass


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
