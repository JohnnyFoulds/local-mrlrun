# Coding Standards

## Introduction

The purpose of this document is to establish coding standards and best practices for developers working on the AI Booster Plus project.

For Python code style, the conventions outlined in the [PEP 8 -- Style Guide for Python Code](https://peps.python.org/pep-0008/) will be followed. This document supplements PEP 8 with additional guidelines specific to the AI Booster Plus project.

Unless explicitly stated otherwise, these standards apply to all repositories under the AI Booster Plus GitLab group.

## Source Control

All code must be committed to the project's [Git repository](https://gitlab.com/vodacomsa/ai-booster-plus) hosted on GitLab.

Developers must apply for the `VcIT_GitLab_AI_Booster_Plus` permission with the `VcIT_GitLab_AI_Booster_Plus_Write` profile via [WhitePages](https://whitepages.ent.vodacom.co.za/).

### Branching Strategy (CI/CD-aligned)

The project uses two long-lived branches:

* `development` is the integration branch for day-to-day work.
* `main` is the release branch and must remain production-ready.

Branching and merging rules:

* `main` and `development` are protected. Direct pushes are not allowed; changes must be merged via merge request (MR).
* Short-lived branches must be used for changes (branch off `development`):
  * `feat/<topic>`, `fix/<topic>`, `refactor/<topic>`, `docs/<topic>`, `chore/<topic>`
* The default target branch for feature work is `development`.
* Promotion to `main` occurs via an MR from `development` to `main` when a release is ready.
* Releases are cut from `main` using tags (e.g., `vX.Y.Z`).
* Hotfixes should branch from `main` (e.g., `hotfix/<topic>`) and be merged back into both `main` and `development`.
* UAT is treated as an environment in CI/CD (not a long-lived `uat` branch). Deployments to UAT and production must be managed via the pipeline and environment rules.

Follow these guidelines for source control:

1. Commit messages must be clear and descriptive, following the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) format:
   `type(scope): subject`
   Example: `feat(auth): add login functionality`.
   Use standard Conventional Commit types such as `feat`, `fix`, `refactor`, `docs`, and `chore`.

2. Use dedicated branches for new features, refactors, or bug fixes. Branch names should reflect the feature or issue being addressed (for example, `feat/auth-login`, `fix/model-serialization`).

3. Regularly pull or rebase from the target branch (`development` for feature work) to keep your branch up to date and minimise merge conflicts.

4. Before merging, ensure that:
   * All automated tests pass (MR pipeline).
   * The code adheres to the coding standards defined in this document and in [PEP 8 -- Style Guide for Python Code](https://peps.python.org/pep-0008/).
   * A merge request (MR) has been reviewed and approved in line with project governance.

## Repository Structure

```text
vodacomsa/
└── ai-booster-plus/                    # Main project group
    ├── Generative AI/                  # Subgroup for Generative AI
    │   ├── aib-genai-tools/
    │   └── aib-genai-utilities/
    ├── Machine Learning/               # Subgroup for Machine Learning
    │   ├── aib-ml-tools/
    │   └── aib-ml-utilities/
    ├── MLRun/                          # Subgroup for MLRun orchestration
    │   ├── aib-mlrun-genai-functions/
    │   ├── aib-mlrun-genai-images/     # Custom Docker images for MLRun GenAI functions
    │   ├── aib-mlrun-ml-functions/
    │   └── aib-mlrun-ml-images/        # Custom Docker images for ML workloads
    ├── ZenML/                          # Subgroup for ZenML pipelines/orchestration
    │   ├── aib-zenml-genai-functions/
    │   ├── aib-zenml-genai-images/     # Custom Docker images for ZenML GenAI pipelines
    │   ├── aib-zenml-ml-functions/
    │   └── aib-zenml-ml-images/        # Custom Docker images for ML pipelines
    └── Discovery Hub/                  # Subgroup for Discovery/Function Hub
````

## References

* [PEP 8 -- Style Guide for Python Code](https://peps.python.org/pep-0008/)
* [Documenting Python Code: A Complete Guide](https://realpython.com/documenting-python-code/)
* [GitLab -- Best practices to set up organizational hierarchies that scale](https://about.gitlab.com/blog/best-practices-to-set-up-organizational-hierarchies-that-scale/)
* [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
* [GitLab -- Branching strategies](https://docs.gitlab.com/user/project/repository/branches/strategies/)
* [GitLab -- Protected branches](https://docs.gitlab.com/user/project/repository/branches/protected/)
* [GitLab CI/CD -- Environments](https://docs.gitlab.com/ci/environments/)
* [GitLab CI/CD -- Merge request pipelines](https://docs.gitlab.com/ci/pipelines/merge_request_pipelines/)
