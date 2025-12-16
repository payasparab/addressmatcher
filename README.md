# AddressMatcher

AddressMatcher is a small library and CLI tool to normalize, compare and score postal addresses. It helps identify duplicate or equivalent addresses that differ by formatting, punctuation, abbreviations, or minor typos. The project is intended to be language- and platform-agnostic and can be used as a library in applications or as a command-line utility.

> NOTE: This README is scaffolded to work with a variety of implementations. If your repository is implemented in a specific language or has a preferred install/build process (npm, pip, Maven, Go modules, etc.), replace the generic steps below with your project's actual commands.

## Table of contents

- [Features](#features)
- [Install](#install)
- [Quick start](#quick-start)
  - [As a library (JavaScript/TypeScript example)](#as-a-library-javascripttypescript-example)
  - [As a CLI](#as-a-cli)
- [API (suggested)](#api-suggested)
- [Configuration options](#configuration-options)
- [Examples](#examples)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- Normalize address strings (case, punctuation, common abbreviations).
- Tokenize and canonicalize components (street, house number, unit, city, postal code, country).
- Compute similarity scores between two addresses.
- Configurable thresholds for match detection.
- CLI for quick comparisons and batch processing.
- Designed to be extensible (custom normalizers, country-specific rules).

## Install

Replace the following with the actual install instructions for your repo.

From source:
```bash
git clone https://github.com/payasparab/addressmatcher.git
cd addressmatcher
# build or install according to project language, for example:
# npm install
# pip install -e .
# mvn package
```

If published to a package registry, add the appropriate install command here (e.g. `npm i @payasparab/addressmatcher`).

## Quick start

Below are example usages. Adapt them to your implementation language.

### As a library (JavaScript/TypeScript example)
```js
// Example: import the module (adjust to actual export)
const { AddressMatcher } = require('@payasparab/addressmatcher');

const matcher = new AddressMatcher({ threshold: 0.85 });

const a = "123 Main St., Apt 4B, New York, NY 10001";
const b = "123 Main Street Apartment 4B New York NY 10001";

const result = matcher.compare(a, b);
console.log(result);
/*
{
  normalizedA: "123 main street apt 4b new york ny 10001",
  normalizedB: "123 main street apt 4b new york ny 10001",
  score: 0.98,
  isMatch: true
}
*/
```

### As a CLI
(Replace with your CLI executable name and flags)
```bash
# Compare two addresses directly
addressmatcher compare "123 Main St., Apt 4B, New York, NY 10001" \
                       "123 Main Street Apartment 4B New York NY 10001" \
                       --threshold 0.9

# Batch compare addresses from files
addressmatcher batch --left addresses_a.csv --right addresses_b.csv --out results.csv
```

## API (suggested)

Below is a suggested API surface. Adapt to the actual functions/classes present in your repo.

- AddressMatcher(options)
  - options:
    - threshold: number (0.0–1.0) — default confidence threshold to consider two addresses a match.
    - country: string — hint for country-specific normalization rules.
    - verbose: boolean — include detailed scoring breakdown.

- normalize(address: string, options?): { normalized: string, components: { street, number, unit, city, postcode, country } }
  - Returns a normalized string and parsed components when possible.

- score(addressA: string, addressB: string, options?): number
  - Returns a similarity score in [0, 1].

- compare(addressA: string, addressB: string, options?): { normalizedA, normalizedB, score, isMatch, details? }
  - Convenience wrapper combining normalize + score + threshold comparison.

- CLI commands:
  - compare <addressA> <addressB> [--threshold]
  - batch --left <file> --right <file> [--out <file>] [--threshold]

## Configuration options

Common options you may want to support:
- threshold: similarity threshold for considering two addresses as the same (default 0.8–0.9).
- country or locale: apply country-specific parsing and abbreviation rules (e.g., US vs UK).
- normalization rules: list of abbreviation expansions (e.g., "St" -> "Street").
- fuzzy: toggle fuzzy token matching (allow small typos).
- ignoreFields: array of fields to ignore in comparisons (e.g., unit, postcode).

## Examples

1) Basic normalization
Input:
- "1600 Amphitheatre Pkwy, Mountain View, CA"
Output:
- "1600 amphitheatre parkway mountain view ca"

2) Fuzzy matching
- "45 Rue de Rivoli, Paris" vs "45 Rue de Rivoli, 75004 Paris" -> high score despite missing postal code.

3) Abbreviation normalization
- "Apt" ⇄ "Apartment", "St" ⇄ "Street", "Rd" ⇄ "Road"

## Testing

Add or run your test suite with:
```bash
# Example commands - replace with actual test commands (npm, pytest, mvn, go test)
# npm test
# pytest
# mvn test
```

Include unit tests for:
- Normalizer edge cases (punctuation, unicode, mixed case)
- Country-specific rules
- Scoring for near-duplicates and clear non-matches
- CLI argument parsing and batch processing

## Contributing

Contributions are welcome. Suggested workflow:
1. Fork the repo
2. Create a branch: git checkout -b feat/my-feature
3. Add tests and documentation for your change
4. Open a pull request describing the change and why it's needed

Please follow the project's coding style and add tests for new behavior.

## License

Specify your license here, e.g.:

This project is licensed under the MIT License — see the LICENSE file for details.

## Contact

Maintainer: payasparab
- GitHub: [@payasparab](https://github.com/payasparab)
- For issues and feature requests: open an issue on this repository.

## Acknowledgements

- Any libraries, datasets or tooling that inspired or were used by this project.

---

If you'd like, I can:
- tailor the README to your repository's actual language and install/build commands (Node, Python, Java, etc.),
- add badges (CI, coverage, npm/pypi) and examples using real exported functions/CLI flags from your code,
- or generate a short CONTRIBUTING.md and CODE_OF_CONDUCT.md.

Tell me which you'd prefer and I'll update the README accordingly.