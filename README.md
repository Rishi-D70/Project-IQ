# ContractIQ  
**Local AI System for Contract Understanding & Cross-Document Intelligence**

Video - https://drive.google.com/file/d/1J2JIDNkhjIDVbTbfC3PK7gZ5QIXSfe9Z/view?usp=sharing

## Problem
Contract review is slow, manual, and error-prone. Legal and compliance teams spend hours searching through long documents to identify **obligations, deadlines, penalties, and responsibilities**. When multiple contracts are involved, tracking inconsistencies or missing clauses becomes even harder.  
Most existing AI tools solve this by sending documents to the cloud, which introduces **privacy, compliance, and cost issues**—unacceptable for sensitive legal data.

## What ContractIQ Does
**ContractIQ** is a **local-first AI contract intelligence system** that analyzes contracts on the user’s machine and converts unstructured legal text into **structured, queryable information**.  
It allows users to ask direct questions, extract key clauses, and derive insights across multiple documents—without uploading data to external servers.

## Key Capabilities
- **Clause-Aware Querying**  
  User questions are mapped to specific contract sections instead of full-document guessing, reducing irrelevant responses.

- **Obligation & Responsibility Extraction**  
  Automatically identifies who must do what, under which conditions, and by when—presented in structured form.

- **Deterministic + LLM Hybrid Parsing**  
  Combines rule-based filtering with local LLM reasoning to improve consistency on legal language.

- **Cross-Document Clause Matching**  
  Detects similar or conflicting clauses across multiple contracts to highlight missing or inconsistent terms.

- **Structured Outputs for Review**  
  Converts free-form legal text into tables and summaries that can be quickly scanned or verified.

- **Local-Only Execution**  
  All processing happens on-device; no document or query data leaves the system.

  ## System Overview
**Workflow**
Contract Upload / User Query
➤
Text Cleaning & Segmentation
➤
Local LLM + Rule-Assisted Parsing
➤
Clause & Entity Extraction
➤
Structured Intelligence Output

## Core Modules
- **Document Ingestion**  
  Handles contract input, preprocessing, and segmentation.

- **Query Handling Engine**  
  Interprets user questions and maps them to relevant contract sections.

- **Information Extraction Layer**  
  Identifies legally significant elements such as obligations, deadlines, and responsibilities.

- **Cross-Document Intelligence (Optional)**  
  Enables comparison across multiple contracts to detect overlaps, gaps, or conflicts.

## Tech Stack
- **Backend:** Python  
- **Frontend:** HTML, CSS, JavaScript  
- **AI Models:** Local LLM - Qwen 2.5 | 7B q4
- **Processing:** Hybrid LLM + rule-based extraction  
- **Execution:** Fully local desktop setup

## Demo Usage
- Upload a contract document  
- Ask queries like:
- “What are the payment obligations?”
- “List all deadlines and penalties”
- View extracted clauses and structured outputs  
- (Optional) Upload multiple contracts to compare insights

## Limitations
- Performance depends on local hardware
- Scanned PDFs rely on text quality
- Not a replacement for legal judgment—decision support only

## Future Enhancements
- Clause risk scoring
- Timeline visualization
- Better multi-contract reasoning
- Legal-domain fine-tuned models
- Scalable indexing for large repositories

## Why ContractIQ Matters
ContractIQ demonstrates that **practical legal intelligence can be built locally**, without compromising data privacy. It bridges raw LLM capability with structured document intelligence, making contract review faster, clearer, and more reliable.

---

**Project Focus:** Privacy-first document intelligence using local AI  
**Status:** Functional prototype with extensible architecture
