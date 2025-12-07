# GitHub Copilot & Contributor Instructions

This file instructs Copilot-assisted development and contributor behavior for this Spec-Driven repo.

## Goals for Copilot/AI-assisted workflows
- Use Copilot to generate boilerplate code (Docusaurus pages, FastAPI endpoints, Qdrant client code, embedding pipeline).
- Use Claude Code subagents via Spec-Kit Plus to generate complex content (chapter drafting, translations, personalization policies).
- Use Copilot to provide test scaffolding and unit tests; always review and run tests locally.

## Branching / Commit Conventions
- Branches:
  - feat/<short-desc>
  - fix/<short-desc>
  - chore/<short-desc>
  - docs/<short-desc>
- Commit messages:
  - Use Conventional Commits style:
    - feat(spec): add rag indexing pipeline (SPEC-020)
    - fix(api): correct selection-mode enforcement (SPEC-032)
  - Include the relevant SPEC-### in the commit body when applicable.
- PR Titles:
  - <type>(SPEC-###): short description
  - Example: feat(SPEC-020): implement ingestion pipeline and qdrant client

## PR Template (copy to .github/PULL_REQUEST_TEMPLATE.md)
- Summary of changes
- Linked tasks and spec IDs
- How to test locally
- Test coverage / results
- Screenshots or demo link
- Checklist:
  - [ ] Linted
  - [ ] Tests added
  - [ ] Spec updated
  - [ ] Docs updated
  - [ ] Reviewed by X

## How to use Spec-Kit Plus & Claude Code (practical instructions)
- Update spec.md repository field to your owner/repo.
- Use Spec-Kit Plus to convert spec.md problem_statement into actionable branch + PR:
  - Provide the problem_statement exactly as written in spec.md.
  - Provide base_ref if you want the PR against a branch other than main.
- For complex content (chapters), use Claude Code to generate:
  - Chapter outlines (prompt: "Using the course curriculum and learning outcomes, generate a chapter outline for X with learning objectives, 3 exercises, and one quiz.")
  - Translation subagent (prompt: "Translate chapter content to Urdu with domain-specific technical terms preserved and glossary entries.")
- When Copilot generates code, do:
  - Run static analysis and linter.
  - Add tests.
  - Annotate where Copilot code needs human review.

## Local Dev & Quick Commands
- Setup virtual env:
  - python -m venv .venv && source .venv/bin/activate
  - pip install -r requirements.txt
- Run backend:
  - uvicorn app.main:app --reload
- Index sample docs:
  - python scripts/ingest_to_qdrant.py --docs ./docs --collection physical_ai_humanoid_robotics_course

## Security & Secrets
- Never commit secrets; use GitHub Actions secrets.
- Use the following secret names:
  - QDRANT_API_KEY
  - NEON_URL
  - BETTER_AUTH_CLIENT_ID
  - BETTER_AUTH_CLIENT_SECRET
  - OPENAI_API_KEY (or CLAUDE_API_KEY)
- For Copilot: be mindful that Copilot will not have your secrets; use placeholders in code and fetch secrets from environment in runtime.

## Example Prompts for Generating Chapters (use with Claude Code or Copilot)
- "Write a 1500-word Chapter: 'ROS 2 Nodes, Topics, Services' with examples in rclpy and a lab exercise to create a publisher & subscriber. Include code blocks and expected output for Ubuntu 22.04 and ROS 2 Humble/Iron."
- "Create 5 multiple-choice questions and 3 coding exercises for 'Gazebo URDF basics'. Each coding exercise should have a rubric and expected output."
- "Generate a concise README describing how to run the RAG pipeline locally, including commands and debug tips for Qdrant ingestion."

## Copilot Review Checklist
- Correctness: run code to verify.
- Security: ensure inputs validated (no arbitrary LLM prompt injection).
- Testability: include tests or describe manual test steps.
- Documentation: update README and docs/ with usage.
- Reusability: prefer small, testable functions and subagent APIs.

## Using Copilot to Build Tests
- Always ask Copilot to produce tests for any new function or endpoint.
- Example prompt to Copilot: "Create pytest unit tests for the FastAPI /api/retrieve endpoint that mocks Qdrant retrieval and asserts the response format."

## Onboarding New Contributors
- Run `make setup` (if present) to prepare local environment.
- Read this repo's spec.md and tasks.md to pick tasks.
- Before opening a PR, run `pre-commit` and tests.
