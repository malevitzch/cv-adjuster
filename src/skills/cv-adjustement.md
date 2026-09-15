# CV Adjustment

## Purpose

Create a one-page CV in LaTeX, tailored to the supplied job offer. Select and phrase
the candidate's strongest evidence from the CV and the supporting materials, while preserving the
original template layout.

## Sandbox layout

The sandbox provides these input directories:

- `/workspace/raw/` contains the Markdown-converted, cleaned source
  achievements. Use it as supporting evidence when a summary is ambiguous or
  lacks necessary context, but avoid reading the files there since they are possibly large.
- `/workspace/information/` contains the achievement-summary library. Treat it
  as the primary information source (along with the sample CV) choosing accomplishments and qualifications.
- `/workspace/offer/` contains the target job offer. Read every supplied file
  to identify the relevant qualifications. Don't be discouraged if a candidate
  is not a perfect match (certain requirements are not met) but do not invent qualifications.
- `/workspace/cv/` contains the current CV's LaTeX template and every file it
  needs to compile. It is the source of the candidate's existing CV structure,
  identity details, and presentation. Use it as a starting point for the tailored CV.

Write deliverables only to `/workspace/output/`: a tailored `.tex` CV, its
compiled `.pdf`, and any template assets that must accompany the `.tex` file to
compile it. Do not alter the input directories. Put unresolved contradictions,
missing source support, or validation failures in `/workspace/logs/`.

The sandbox image provides the template's LaTeX compiler and dependencies,
plus a PDF page-count utility such as `pdfinfo`. If it also provides a PDF
renderer, use it for a final visual inspection. If any of those things appear to be missing, report the issue in `/workspace/logs/` and finish without running any other final checks. 

## Evidence and tailoring rules

- Use only claims supported by `/workspace/information/`, the existing CV, or
  `/workspace/raw/`, but only in the case that `workspace/information/` is insufficient.
- Do not invent skills, metrics, titles, dates, qualifications, seniority, or
  employer/project ownership. Do not represent desired or planned work as
  completed work.
- Map the offer's requirements to supported evidence, finding the best match for each requirement
  if one exists. Prefer using `/workspace/information/` over `/workspace/raw/` for evidence, only 
  resort to `/workspace/raw/` when the summary is ambiguous or lacks necessary context and there
  are hopes of finding it in the raw files. If no evidence exists, do not invent it; record the missing evidence in `/workspace/logs/` so that the candidate can possibly address it themselves.
- Tailoring may reorder experience, choose/rewrite bullets for clarity, and
  prioritize relevant projects and skills. It must not change the factual
  meaning, scope, or attribution of an accomplishment.
- Keep the general CV sections represented in the template, especially work
  experience and education, even when they are not explicitly mentioned in the offer.
  Do not remove a whole general-history section merely to make room
  for tailored content. Preserve the candidate's contact/header information.

## Template and length requirements

Use the LaTeX template from `/workspace/cv/` as the starting point. Preserve
its document class, packages, custom commands, page geometry, typography,
styling, and section structure. Adapt its content rather than replacing it with
a new template or altering layout settings to force a fit.

The tailored CV must compile to exactly one PDF page. When it is too long,
reduce content before changing presentation: remove lower-value bullets, combine
overlapping facts, and tighten wording without losing material meaning. Do not 
resort to shrinking fonts or compressing margins unless it's absolutely necessary.

## Workflow

1. Find the CV document in `/workspace/cv/` and read the job offer in `/workspace/offer/`. 
2. Identify the offer's high-priority requirements and select the best supported
   evidence. Retain the CV's general sections and use the offer's terminology
   only where it accurately describes the candidate's experience.
3. Copy the template into `/workspace/output/` and make the
4. Compile the output with the template's normal LaTeX toolchain. Resolve
   compilation errors and meaningful warnings (including missing assets,
   undefined references, and visible overflow). Compile again when LaTeX needs
   a second pass for references or layout.
5. Verify the generated PDF has exactly one page, for example with
   `pdfinfo`. Inspect it visually when rendering tools are available to confirm
   that no text is clipped, overlapping, unreadable, or pushed onto a second
   page. If it does not fit, revise the content and repeat the compile-and-check
   cycle. Do not report success without a successful one-page PDF check.

## Final check

Before finishing, ensure that:

- the output contains a compiling `.tex` file and the corresponding one-page
  PDF
- every tailored claim is supported by the supplied evidence
- the current CV's general sections, including work experience and education,
  remain present
- the visual LaTeX template has not been redesigned or compressed to force a
  fit and is exactly one page long
- any unresolved evidence issue or inability to perform the PDF validation is
  documented in `/workspace/logs/`.
