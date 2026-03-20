---
name: qa
description: "Quality assurance verdict for any artifact"
---

# /ouroboros:qa

General-purpose quality assurance verdict for any artifact type.

## Usage

```
/ouroboros:qa <artifact> [pass_criteria]
```

**Trigger keywords:** "qa this", "check quality", "verify this"

## How It Works

The QA tool evaluates any artifact (code, text, JSON, etc.) against pass/fail criteria and returns a structured verdict.

### Path A — MCP Mode (Preferred)

If `ouroboros_qa` MCP tool is available:

1. Call `ouroboros_qa` with:
   - `artifact`: The content to evaluate
   - `pass_criteria`: What "pass" means (natural language)
   - `reference` (optional): Expected output or reference for comparison
   - `pass_threshold` (optional): Score threshold, default 0.80

2. The tool returns a structured JSON verdict:
   - `verdict`: PASS / REVISE / FAIL
   - `score`: 0.0–1.0 quality score
   - `dimensions`: Per-dimension scores (correctness, completeness, style, etc.)
   - `differences`: Specific issues found
   - `suggestions`: Actionable improvements
   - `reasoning`: Explanation of assessment

3. Based on verdict:
   - **PASS** (score ≥ threshold): Artifact meets criteria
   - **REVISE** (score ≥ threshold - 0.15): Minor improvements needed, show suggestions
   - **FAIL** (score < threshold - 0.15): Significant issues, show differences and suggestions

### Path B — Plugin Fallback

If MCP tool is not available, perform manual QA:

1. Read the artifact content
2. Evaluate against the provided pass criteria
3. Score each dimension (correctness, completeness, consistency, clarity)
4. Provide structured feedback with specific suggestions

## Examples

```
ooo qa          # QA the most recent execution output
ooo qa <file>   # QA a specific file
ooo qa <code> "All functions must have docstrings"  # QA with custom criteria
```

## Iterative Usage

QA is designed for loop usage. After receiving a REVISE verdict:
1. Apply the suggestions
2. Re-run `ooo qa` with the same criteria
3. Repeat until PASS
