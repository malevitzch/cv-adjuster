# Summarize Achievements

## Purpose

Turn provided Markdown into an achievement library. The library is an intermediate
retrieval corpus: a later agent should be able to select relevant accomplishments
for a job description without rereading a full CV, paper, or portfolio.

This library is not a CV yet - the summary should avoid colorization or spinning narratives and just provide cold, hard facts that can be later used to create a resume by picking the correct ones and adding a spin to them.

## Scope

Read every `*.md` file in the supplied input directory, including nested files.
Inputs can include CVs, project descriptions, papers, performance reviews,
certificates, and overlapping versions of the same material. Treat the content as
candidate evidence, not necessarily as a claim that the candidate authored or
personally achieved every fact in it. Sometimes, the context for a certain file 
might be found in another file, so be wary of that.

Write only Markdown files beneath the supplied output directory. Do not alter,
move, or copy input documents into the output. 

## What to extract

Extract items that may help substantiate a future application, including:

- measurable results, delivered outcomes, awards, and publications;
- projects, research, products, systems, processes, and improvements the candidate
  is explicitly connected to;
- roles, responsibilities, leadership, collaboration, and domain experience when
  they establish relevant capability;
- tools, methods, languages, certifications, education, and other qualifications
  when explicitly stated.

Prefer an accomplishment stated as **action + object + result/impact + context + technology**.
Keep useful supporting experience even when no metric or outcome is supplied; do
not discard it merely because it is weaker than an achievement.

## Evidence rules

- Do not infer personal ownership from a team, employer, laboratory, paper, or
  product claim. For a co-authored paper, say that the candidate co-authored it;
  only describe a particular contribution if the source attributes it to them.
- Do not turn duties into results, technologies mentioned in a document into skills
  possessed by the candidate, or future plans into completed work.
- Resolve obvious duplicate copies into one card and cite all supporting sources.
  If sources disagree, retain the conflict in the relevant card rather than choosing
  a value or silently merging claims.
- Omit information that is only contact data, formatting, boilerplate, references,
  or unrelated document prose. Never include sensitive personal details unless they
  are essential to the achievement itself.

## Output layout

TODO: 

## Workflow

1. Inventory all input Markdown and identify which documents are CV-like,
   portfolio/project-like, publications, or duplicates. Read enough surrounding
   context to determine the candidate's relation to each claim.
2. Extract candidate-linked evidence, normalize obvious formatting variation, and
   group it into independently retrievable cards. Combine corroborating evidence
   from several files while preserving provenance.
3. Write the cards and index. Compress aggressively by removing background and
   repetition, not by dropping attribution, scope, metrics, limitations, or source
   links.
4. Review the output against the source: every number and claim must be traceable;
   cards must be distinct, self-contained, and useful without the original CV; and
   no input files or raw copies should appear in the output.

## Final check

Before finishing, ensure that:

- all input Markdown files were considered;
- no achievement overstates the candidate's role or converts an aspiration into a
  result;
- each card has source notes and retrieval terms, and each card appears in the
  index;