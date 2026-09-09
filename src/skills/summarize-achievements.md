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

Write only Markdown files beneath the /workspace/output directory. Do not alter,
move, or copy input documents into the output. 

## What to extract

Extract items that may help substantiate a future application, including:

- measurable results, delivered outcomes, awards, and publications
- projects, research, products, systems, processes, and improvements the candidate
  is explicitly connected to
- roles, responsibilities, leadership, collaboration, and domain experience when
  they establish relevant capability
- tools, methods, languages, certifications, education, and other qualifications
  when explicitly stated

## Evidence rules

- Do not infer personal ownership from a team, employer, laboratory, paper, or
  product claim. For a co-authored paper, say that the candidate co-authored it;
  only describe a particular contribution if the source attributes it to them.
- Do not turn duties into results, technologies mentioned in a document into skills
  possessed by the candidate, or future plans into completed work.
- If any information is contradictory, put a written report in /workspace/logs.
- Omit information that is only contact data, formatting, boilerplate, references,
  or unrelated document prose. Never include sensitive personal details unless they
  are essential to the achievement itself.

## Output layout

The output should be a set of markdown files, each containing a single relevant fact that could be used in a resume. This includes things such as projects, publications, awards, work experience, certificates, education, and possibly relevant coursework. The files should be written in a way that they can later be easily searched with a vector database.

## Workflow

1. Inventory all input Markdown and identify which documents are CV-like,
   portfolio/project-like, publications, or duplicates. Read enough surrounding
   context to determine the candidate's relation to each claim.
2. Extract candidate-linked evidence, normalize obvious formatting variation, and
   group it into independently retrievable files. The output structure of the files should be a
   flat list, not a hierarchy. Furthermore, it does not have to match the input structure whatsoever.
3. Write the cards and index. Compress aggressively by removing information that is not relevant in a resume.
   Note that it's important to preserve info which would be useful for the same experience if approached from a different angle. For example, if a project description mentions a specific technology, it may be useful to keep that mention even if the candidate's role in the project is not clear.
4. Esure that the output is factually accurate by comparing the output against the input files.

## Final check

Before finishing, ensure that:

- All input Markdown files were considered
- No achievement overstates the candidate's role or converts an aspiration into a
  result
- Each output file contains a reasonable piece of information that could be put in a resume 