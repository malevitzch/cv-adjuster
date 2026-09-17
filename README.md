# cv-adjuster
An LLM-powered tool that can be used to automatically adjust your CV to job offers, 
picking the relevant qualifications that the user has and creating a version of the CV
tailored to the job description.

## CV adjustment

Use `cv-adjust` with the cleaned source evidence, summary library, job offer,
existing LaTeX CV template, and an output directory:

```bash
cv-adjust RAW_DIR INFORMATION_DIR OFFER_DIR CV_DIR OUTPUT_DIR [--logs LOGS_DIR] [-v]
```

The command runs the CV-adjustment agent in a LaTeX-enabled isolated container.
It writes the tailored `.tex` file, its one-page PDF, and required template
assets to `OUTPUT_DIR`. Validation and unresolved-evidence notes go to
`LOGS_DIR`, or to `logs` next to `OUTPUT_DIR` when `--logs` is omitted.
