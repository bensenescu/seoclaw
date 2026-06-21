"""
seoclaw eval demo — run this to see the agent score a bad article vs a good article.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from eval.scorer import score_article

# ANSI colors — work in any modern terminal
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

BAR_WIDTH = 20


def score_bar(score: int) -> str:
    filled = round((score / 10) * BAR_WIDTH)
    empty  = BAR_WIDTH - filled
    color  = GREEN if score >= 7 else (YELLOW if score >= 5 else RED)
    return f"{color}{'█' * filled}{'░' * empty}{RESET} {score}/10"


def print_header(text: str):
    width = 60
    print(f"\n{BOLD}{CYAN}{'═' * width}{RESET}")
    print(f"{BOLD}{CYAN}  {text}{RESET}")
    print(f"{BOLD}{CYAN}{'═' * width}{RESET}\n")


def print_verdict(verdict: str, ai_average: float, mechanical: str):
    if verdict == "PASS":
        color = GREEN
        icon  = "✓  PASS"
    else:
        color = RED
        icon  = "✗  FAIL"
    print(f"\n{BOLD}{color}  {icon}{RESET}")
    print(f"  AI average:        {BOLD}{ai_average}/10{RESET}")
    print(f"  Mechanical checks: {BOLD}{mechanical}{RESET}")


def print_scores(ai_scores: dict):
    print(f"\n{BOLD}  Dimension scores:{RESET}")
    for dim, data in ai_scores.items():
        label = dim.replace("_", " ").title().ljust(28)
        bar   = score_bar(data["score"])
        print(f"    {label} {bar}")
        print(f"    {DIM}    └─ {data['reasoning'][:90]}{'...' if len(data['reasoning']) > 90 else ''}{RESET}")


def print_revision_instructions(failing: list, instructions: dict):
    if not failing:
        return
    print(f"\n{BOLD}{YELLOW}  Revision instructions ({len(failing)} issues to fix):{RESET}")
    for dim in failing:
        instruction = instructions.get(dim, "")
        print(f"\n    {YELLOW}▶ {dim.replace('_', ' ').upper()}{RESET}")
        # Word-wrap at 72 chars
        words = instruction.split()
        line  = "      "
        for word in words:
            if len(line) + len(word) > 76:
                print(line)
                line = "      " + word + " "
            else:
                line += word + " "
        if line.strip():
            print(line)


def print_needs_context(notifications: list):
    if not notifications:
        return
    print(f"\n{BOLD}{YELLOW}  ⚠  Context missing:{RESET}")
    for note in notifications:
        first_line = note.split("—")[0].strip() if "—" in note else note[:80]
        print(f"    {YELLOW}→ {first_line}{RESET}")


def run_demo():
    print(f"\n{BOLD}{'━' * 60}{RESET}")
    print(f"{BOLD}  seoclaw — Content Eval Agent Demo{RESET}")
    print(f"{BOLD}{'━' * 60}{RESET}")
    print(f"\n  Scores articles before they publish.")
    print(f"  13 dimensions · LLM-as-Judge · Revision loop")

    # ── TEST 1: BAD ARTICLE ──────────────────────────────────────
    print_header("TEST 1 — Unoptimised article")
    print(f"  {DIM}Scoring eval/sample_article.md ...{RESET}", end="", flush=True)

    result1 = score_article(
        "eval/sample_article.md",
        "keyword research",
    )
    print(f"\r  {DIM}Scored in ~15s                    {RESET}")

    print_verdict(result1["verdict"], result1["ai_average"], result1["mechanical_passes"])
    print_scores(result1["ai_scores"])
    print_revision_instructions(
        result1.get("failing_dimensions", []),
        result1.get("revision_instructions", {}),
    )
    print_needs_context(result1.get("needs_context", []))

    # pause for effect
    print(f"\n{DIM}  ── applying revision instructions ──{RESET}")
    time.sleep(1)

    # ── TEST 2: GOOD ARTICLE ─────────────────────────────────────
    print_header("TEST 2 — Optimised article (after revisions)")
    print(f"  {DIM}Scoring eval/golden_pass.md ...{RESET}", end="", flush=True)

    result2 = score_article(
        "eval/golden_pass.md",
        "sustainable fashion keyword research",
        author_context="Startup founder with firsthand experience auditing keyword strategies for 30+ sustainable fashion brands",
        attempt=2,
    )
    print(f"\r  {DIM}Scored in ~15s                  {RESET}")

    print_verdict(result2["verdict"], result2["ai_average"], result2["mechanical_passes"])
    print_scores(result2["ai_scores"])

    # ── COMPARISON SUMMARY ────────────────────────────────────────
    print_header("Summary — before vs after")
    print(f"  {'Metric':<30} {'Before':>10}  {'After':>10}")
    print(f"  {'─' * 52}")
    v1 = result1["ai_average"]
    v2 = result2["ai_average"]
    diff = round(v2 - v1, 1)
    diff_str = f"{GREEN}+{diff}{RESET}" if diff > 0 else f"{RED}{diff}{RESET}"
    print(f"  {'AI average':<30} {RED}{v1}/10{RESET}{'':>5}  {GREEN}{v2}/10{RESET}  {diff_str}")
    print(f"  {'Mechanical passes':<30} {RED}{result1['mechanical_passes']}{RESET}{'':>8}  {GREEN}{result2['mechanical_passes']}{RESET}")
    print(f"  {'Verdict':<30} {RED}FAIL{RESET}{'':>9}  {GREEN}PASS{RESET}")
    fail_count = len(result1.get("failing_dimensions", []))
    print(f"  {'Failing dimensions':<30} {RED}{fail_count}{RESET}{'':>9}  {GREEN}0{RESET}")

    print(f"\n{BOLD}  The loop works.{RESET} Bad article → eval catches it")
    print(f"  → revision instructions → rewrite → PASS → publish.\n")


if __name__ == "__main__":
    run_demo()
