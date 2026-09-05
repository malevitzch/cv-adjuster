# Data Correction

## Purpose

Transform MarkItDown output into clean output containing information only, 
removing formatting artifacts and metadata.
The goal is to preserve the information in the documents, stripping away 
anything related to the formatting or layout, unless it is necessary to convey meaning.

## Scope

This skill applies to extracted content from PDFs, resumes, TeX documents,
papers, and other unstructured candidate-source files. The input may contain
garbled text, accidental tables, repeated page furniture, and document metadata. 
Do not touch any files that are not Markdown.

## Task

Correct the extracted Markdown files so that they are readable and contain only information relevant to it's contents

1. Identify the documents' structure and content. Determin whether there is any data only relevant to the layout of the original document and if there are any obvious extraction artifacts.
2. Replace broken tables and fragmented multi-column layouts with semantic Markdown. Only ever leave tables if they are semantically meaningful and contain information that cannot be conveyed in a simpler format. Otherwise, convert tables to lists or paragraphs.
3. Never add any additional information not present in the original document. Do not make things up or infer anything.

## Final Check

Before finishing, ensure that:

- All documents in the directory have been processed and cleaned properly.
- There are no formatting artifacts such as broken tables, split words, awkward line breaks, or metadata.
- Parsing the contents of the documents does not require any deeper reasoning or interpretation beyond that needed to understand the information presented.