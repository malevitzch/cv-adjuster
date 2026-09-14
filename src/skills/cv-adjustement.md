# CV Adjustment

## Purpose

Create a truthful, one-page CV tailored to the supplied job offer. Select and
phrase the candidate's strongest relevant evidence, while preserving the
provided CV's LaTeX design and the broadly useful parts of their history.

## Sandbox layout

The sandbox provides these input directories:

- `/workspace/raw/` contains the Markdown-converted, cleaned source
  achievements. Use it as supporting evidence when a summary is ambiguous or
  lacks necessary context.
- `/workspace/information/` contains the achievement-summary library. Treat it
  as the primary corpus for choosing accomplishments and qualifications.
- `/workspace/offer/` contains the target job offer. Read every supplied file
  to identify the role's essential requirements, preferred qualifications,
  terminology, and language.
- `/workspace/cv/` contains the current CV's LaTeX template and every file it
  needs to compile. It is the source of the candidate's existing CV structure,
  identity details, and presentation.

Write deliverables only to `/workspace/output/`: a tailored `.tex` CV, its
compiled `.pdf`, and any template assets that must accompany the `.tex` file to
compile it. Do not alter the input directories. Put unresolved contradictions,
missing source support, or validation failures in `/workspace/logs/`.

The sandbox image must provide the template's LaTeX compiler and dependencies,
plus a PDF page-count utility such as `pdfinfo`. If it also provides a PDF
renderer, use it for a final visual inspection.

## Evidence and tailoring rules

- Use only claims supported by `/workspace/information/`, the existing CV, or
  `/workspace/raw/`. The summary library makes retrieval easier; it does not
  turn an unverified team claim into a personal achievement.
- Do not invent skills, metrics, titles, dates, qualifications, seniority, or
  employer/project ownership. Do not represent desired or planned work as
  completed work.
- Resolve apparent conflicts against the raw evidence and current CV where
  possible. If they cannot be resolved, do not guess or silently merge them;
  record the conflict in `/workspace/logs/` and use only the non-conflicting
  information.
- Map the offer's requirements to supported evidence. Prefer concrete outcomes,
  relevant responsibilities, tools, methods, domain experience, and education
  over generic keyword lists. A requirement with no support must remain absent;
  never manufacture a match or call attention to the gap.
- Tailoring may reorder experience, choose/rewrite bullets for clarity, and
  prioritize relevant projects and skills. It must not change the factual
  meaning, scope, or attribution of an accomplishment.
- Keep the general CV sections represented in the template, especially work
  experience and education, even when the offer makes another section more
  prominent. Do not remove a whole general-history section merely to make room
  for tailored content. Preserve the candidate's contact/header information
  unless the source itself requires a correction.

## Template and length requirements

Use the LaTeX template from `/workspace/cv/` as the starting point. Preserve
its document class, packages, custom commands, page geometry, typography,
styling, and section structure. Adapt its content rather than replacing it with
a new template or altering layout settings to force a fit.

The tailored CV must compile to exactly one PDF page. When it is too long,
reduce content before changing presentation: remove lower-value bullets, combine
overlapping facts, and tighten wording without losing material meaning. Do not
shrink fonts, margins, spacing, or use manual negative spacing to meet the
one-page requirement. If the provided template contains configurable content
limits, use them normally rather than changing the template's visual design.

## Workflow

1. Inventory the offer, the LaTeX template and its compile entry point, the
   achievement summaries, and the raw evidence needed to disambiguate selected
   claims. Determine which document is the actual editable CV source before
   editing anything.
2. Identify the offer's high-priority requirements and select the best supported
   evidence. Retain the CV's general sections and use the offer's terminology
   only where it accurately describes the candidate's experience.
3. Copy the template into `/workspace/output/` and make the smallest content
   edits necessary to produce the tailored CV. Keep any required local assets
   and compile paths intact.
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
  PDF;
- every tailored claim is supported by the supplied evidence;
- the current CV's general sections, including work experience and education,
  remain present;
- the visual LaTeX template has not been redesigned or compressed to force a
  fit; and
- any unresolved evidence issue or inability to perform the PDF validation is
  documented in `/workspace/logs/`.
