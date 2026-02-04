# Badge Implementation Plan for ci-automation

## Context

The gcovr-development repo has a new badge generation script that creates shields.io-style SVG badges from gcovr HTML output. These badges need to be generated during CI and committed to the ci-automation branch so they can be displayed in the README.

## Files to Add/Modify

### 1. Add `scripts/generate_badges.py`

Python script that:
- Parses gcovr HTML output (index.html) to extract line/function/branch coverage percentages
- Generates SVG badges in shields.io flat style
- Outputs to `badges/` subdirectory: coverage-lines.svg, coverage-functions.svg, coverage-branches.svg
- Uses standard colors: green (>=90%), yellow (>=75%), red (<75%)
- No external dependencies (pure Python)

### 2. Modify `scripts/lcov-jenkins-gcc-13.sh`

Add badge generation step after gcovr runs:

```bash
python3 "path/to/generate_badges.py" "$outputlocation"
```

### 3. Ensure Badges Are Committed

The generated badges in `json/gcovr/badges/` should be committed to the ci-automation branch so they're accessible via:

```
https://raw.githubusercontent.com/cppalliance/gcovr-development/ci-automation/json/gcovr/badges/coverage-lines.svg
```

## Badge Output Structure

```
json/gcovr/
├── index.html
├── badges/
│   ├── coverage-lines.svg
│   ├── coverage-functions.svg
│   ├── coverage-branches.svg
│   └── coverage.json
```

## Reference Implementation

The reference implementation is in the gcovr-development repo on branch `claude/add-readme-badges-64gA9`.

## Badge URL Format

README badges should use these URLs:

```markdown
[![Lines](https://raw.githubusercontent.com/cppalliance/gcovr-development/ci-automation/json/gcovr/badges/coverage-lines.svg)](https://github.com/cppalliance/gcovr-development/tree/ci-automation/json/gcovr)
[![Functions](https://raw.githubusercontent.com/cppalliance/gcovr-development/ci-automation/json/gcovr/badges/coverage-functions.svg)](https://github.com/cppalliance/gcovr-development/tree/ci-automation/json/gcovr)
[![Branches](https://raw.githubusercontent.com/cppalliance/gcovr-development/ci-automation/json/gcovr/badges/coverage-branches.svg)](https://github.com/cppalliance/gcovr-development/tree/ci-automation/json/gcovr)
```
