# Composio 100-App Integration & MCP Research Report

**Total Apps Audited:** 4 | **Verified:** 1 | **Flagged for Review:** 3

## 1. Executive Summary & Buildability Verdict

| Buildability Verdict | Count | Share |
| :--- | :---: | :---: |
| **Yes - Moderate** | 2 | 50% |
| **Yes - Easy Win** | 1 | 25% |
| **Blocked / Gated** | 1 | 25% |
| **Has Official MCP Server** | 0 | 0% |
| **Needs Manual Review (Flagged/Unverified)** | 3 | 75% |

## 2. Pattern Analysis & Clustering

### A. Authentication Dominance
| Auth Method | App Count | Share of Apps |
| :--- | :---: | :---: |
| OAuth2 | 3 | 75% |
| Bearer Token | 1 | 25% |
| API Key | 1 | 25% |
| None/Local CLI | 1 | 25% |

### B. Access Gate Breakdown
| Access Gate | Count | Share |
| :--- | :---: | :---: |
| Paid Plan Required | 1 | 25% |
| Partner / Sales-Gated | 1 | 25% |
| Open Source / Local | 1 | 25% |
| Self-Serve (Free/Trial) | 1 | 25% |

### C. Category Clustering (Self-Serve vs. Gated)
| Category | Total Apps | Self-Serve | Gated / Paid | Easy Wins |
| :--- | :---: | :---: | :---: | :---: |
| CRM & Sales | 2 | 0 | 2 | 0 |
| Data, SEO & Scraping | 1 | 0 | 1 | 1 |
| AI, Research & Media | 1 | 1 | 0 | 0 |

### D. Top Blockers Preventing Immediate Build
| Blocker | Affected Apps |
| :--- | :---: |
| Paid Plan Required | 1 |
| Enterprise sales gate | 1 |
| No public developer API available | 1 |

## 3. Immediate Build Queue - Easy Wins (1 Apps)

| ID | App | Category | Auth Methods | API Surface | Official MCP |
| :---: | :--- | :--- | :--- | :--- | :---: |
| 58 | [Sherlock](https://github.com/sherlock-project/sherlock) | Data, SEO & Scraping | None/Local CLI | CLI/SDK only | No |

## 4. Apps with Official MCP Servers (0 Apps)


## 5. Manual Audit & Verification Queue (3 Apps)

| ID | App | Buildable | Main Blocker | Verification Status |
| :---: | :--- | :--- | :--- | :--- |
| 1 | Salesforce | Yes - Moderate | Paid Plan Required | Flagged (Unreachable URL: ConnectError) |
| 10 | DealCloud | Yes - Moderate | Enterprise sales gate | Flagged (Unreachable URL: ConnectError) |
| 91 | NotebookLM | Blocked / Gated | No public developer API available | DISCREPANCY: The visible page text does not contain any information regarding authentication methods (OAuth2), pricing/access gates (Self-Serve), or API availability. |