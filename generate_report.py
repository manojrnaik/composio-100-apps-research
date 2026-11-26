import json
from collections import Counter, defaultdict
from pathlib import Path

DATA_FILE = Path("data.json")
REPORT_FILE = Path("REPORT.md")


def main():
    if not DATA_FILE.exists():
        print("Error: data.json not found. Run research_agent.py first.")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        apps = json.load(f)

    total = len(apps)
    if total == 0:
        print("Error: data.json is empty.")
        return

    # Core aggregations
    buildable_counts = Counter(a.get("buildable_today", "Unknown") for a in apps)
    gate_counts = Counter(a.get("access_gate", "Unknown") for a in apps)
    
    # Flatten auth methods (handles both list and string formats safely)
    auth_counts = Counter()
    for a in apps:
        methods = a.get("auth_methods", [])
        if isinstance(methods, str):
            methods = [m.strip() for m in methods.split(",") if m.strip()]
        for m in methods:
            auth_counts[m] += 1

    # Common blockers (excluding 'None' or 'N/A')
    blocker_counts = Counter(
        a.get("main_blocker", "None")
        for a in apps
        if a.get("main_blocker") and str(a.get("main_blocker")).lower() not in {"none", "n/a", "no blocker", "-"}
    )

    # Category clustering (Self-serve vs Gated & Easy Wins per category)
    cat_stats = defaultdict(lambda: {"total": 0, "self_serve": 0, "gated": 0, "easy_win": 0})
    for a in apps:
        cat = a.get("category", "Uncategorized")
        gate = str(a.get("access_gate", "")).lower()
        buildable = a.get("buildable_today", "")

        cat_stats[cat]["total"] += 1
        if "self-serve" in gate or "free" in gate or "trial" in gate:
            cat_stats[cat]["self_serve"] += 1
        else:
            cat_stats[cat]["gated"] += 1

        if "easy win" in buildable.lower():
            cat_stats[cat]["easy_win"] += 1

    official_mcps = [a for a in apps if a.get("has_official_mcp")]
    easy_wins = [a for a in apps if "easy win" in str(a.get("buildable_today", "")).lower()]
    flagged = [
        a for a in apps if not str(a.get("verification_status", "")).startswith("VERIFIED")
    ]

    # Build Markdown Report
    lines = [
        "# Composio 100-App Integration & MCP Research Report",
        "",
        f"**Total Apps Audited:** {total} | **Verified:** {total - len(flagged)} | **Flagged for Review:** {len(flagged)}",
        "",
        "## 1. Executive Summary & Buildability Verdict",
        "",
        "| Buildability Verdict | Count | Share |",
        "| :--- | :---: | :---: |",
    ]

    for status, count in buildable_counts.most_common():
        lines.append(f"| **{status}** | {count} | {count / total:.0%} |")

    lines.extend([
        f"| **Has Official MCP Server** | {len(official_mcps)} | {len(official_mcps) / total:.0%} |",
        f"| **Needs Manual Review (Flagged/Unverified)** | {len(flagged)} | {len(flagged) / total:.0%} |",
        "",
        "## 2. Pattern Analysis & Clustering",
        "",
        "### A. Authentication Dominance",
        "| Auth Method | App Count | Share of Apps |",
        "| :--- | :---: | :---: |",
    ])

    for auth, count in auth_counts.most_common():
        lines.append(f"| {auth} | {count} | {count / total:.0%} |")

    lines.extend([
        "",
        "### B. Access Gate Breakdown",
        "| Access Gate | Count | Share |",
        "| :--- | :---: | :---: |",
    ])

    for gate, count in gate_counts.most_common():
        lines.append(f"| {gate} | {count} | {count / total:.0%} |")

    lines.extend([
        "",
        "### C. Category Clustering (Self-Serve vs. Gated)",
        "| Category | Total Apps | Self-Serve | Gated / Paid | Easy Wins |",
        "| :--- | :---: | :---: | :---: | :---: |",
    ])

    for cat, stats in sorted(cat_stats.items(), key=lambda x: x[1]["total"], reverse=True):
        lines.append(
            f"| {cat} | {stats['total']} | {stats['self_serve']} | {stats['gated']} | {stats['easy_win']} |"
        )

    lines.extend([
        "",
        "### D. Top Blockers Preventing Immediate Build",
        "| Blocker | Affected Apps |",
        "| :--- | :---: |",
    ])

    for blocker, count in blocker_counts.most_common():
        lines.append(f"| {blocker} | {count} |")

    lines.extend([
        "",
        f"## 3. Immediate Build Queue - Easy Wins ({len(easy_wins)} Apps)",
        "",
        "| ID | App | Category | Auth Methods | API Surface | Official MCP |",
        "| :---: | :--- | :--- | :--- | :--- | :---: |",
    ])

    for a in easy_wins:
        methods = a.get("auth_methods", [])
        auth = ", ".join(methods) if isinstance(methods, list) else str(methods)
        mcp = "Yes" if a.get("has_official_mcp") else "No"
        url = a.get("evidence_url", "#")
        lines.append(
            f"| {a.get('id', '-')} | [{a.get('name', 'Unknown')}]({url}) | {a.get('category', '-')} | {auth} | {a.get('api_surface', '-')} | {mcp} |"
        )

    lines.extend([
        "",
        f"## 4. Apps with Official MCP Servers ({len(official_mcps)} Apps)",
        "",
    ])

    for a in official_mcps:
        notes = a.get("mcp_notes") or "Official MCP server documented."
        lines.append(f"- **{a.get('name', 'Unknown')}** ({a.get('category', '-')}): {notes}")

    lines.extend([
        "",
        f"## 5. Manual Audit & Verification Queue ({len(flagged)} Apps)",
        "",
        "| ID | App | Buildable | Main Blocker | Verification Status |",
        "| :---: | :--- | :--- | :--- | :--- |",
    ])

    for a in flagged:
        lines.append(
            f"| {a.get('id', '-')} | {a.get('name', 'Unknown')} | {a.get('buildable_today', '-')} | {a.get('main_blocker', 'None')} | {a.get('verification_status', 'Unverified')} |"
        )

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Success! Generated {REPORT_FILE} ({total} apps processed).")


if __name__ == "__main__":
    main()
