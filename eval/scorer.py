import os
import re
import json
from pathlib import Path
import anthropic

# Score threshold below which a dimension is considered failing
FAIL_THRESHOLD = 6
# Minimum AI average to pass
AI_PASS_THRESHOLD = 7.0
# Hallucination must be at least this to pass
HALLUCINATION_PASS_THRESHOLD = 7
# At least this many mechanical checks must pass
MECHANICAL_PASS_REQUIRED = 3


def load_env():
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

load_env()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def _extract_meta_description(markdown: str) -> str:
    """Pull meta description from YAML frontmatter, if present."""
    if not markdown.startswith("---"):
        return ""
    end = markdown.find("---", 3)
    if end == -1:
        return ""
    frontmatter = markdown[3:end]
    for line in frontmatter.splitlines():
        lower = line.lower()
        if lower.startswith("description:") or lower.startswith("meta_description:"):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    return ""


def _check_missing_context(markdown: str, keyword: str, author_context: str) -> list[str]:
    """
    Detect what context is missing that would make the eval more accurate.
    Returns a list of notifications to surface to the user.
    These are non-blocking — the eval still runs, but the pipeline/user
    should provide this info on the next attempt for better results.
    """
    notifications = []

    if not author_context:
        notifications.append(
            "CONTEXT NEEDED — No author context provided. For more accurate scoring on "
            "'originality' and 'source_quality', pass who is writing this and their "
            "background (e.g. 'founder with 5 years in fashion', 'agency writer', "
            "'researcher'). Firsthand experience counts as valid authority."
        )

    word_count = len(markdown.split())
    if word_count < 400:
        notifications.append(
            f"POSSIBLE DRAFT — Article is only {word_count} words. Minimum for SEO is 800. "
            "If this is a draft, scores will be low. Pass a complete article for a meaningful eval."
        )

    if not _extract_meta_description(markdown):
        notifications.append(
            "MISSING META DESCRIPTION — Add a 150-160 character meta description in YAML "
            "frontmatter at the top of the file:\n"
            "---\n"
            f'description: "Your description containing {keyword} here..."\n'
            "---"
        )

    return notifications


def mechanical_checks(markdown: str, keyword: str) -> dict:
    """Rule-based checks that don't need an LLM."""
    word_count = len(markdown.split())
    headings = re.findall(r"^#{1,3} .+", markdown, re.MULTILINE)
    h1 = [h for h in headings if h.startswith("# ")]
    h2 = [h for h in headings if h.startswith("## ")]
    h3 = [h for h in headings if h.startswith("### ")]
    links = re.findall(r"\[.+?\]\(.+?\)", markdown)
    keyword_count = markdown.lower().count(keyword.lower())
    keyword_density = round((keyword_count / word_count) * 100, 2) if word_count else 0

    meta_desc = _extract_meta_description(markdown)
    meta_desc_length = len(meta_desc)
    meta_desc_has_keyword = keyword.lower() in meta_desc.lower() if meta_desc else False

    return {
        "word_count": word_count,
        "word_count_pass": word_count >= 800,
        "h1_count": len(h1),
        "h2_count": len(h2),
        "h3_count": len(h3),
        "heading_structure_pass": len(h1) == 1 and len(h2) >= 2,
        "link_count": len(links),
        "keyword_density_percent": keyword_density,
        "keyword_density_pass": 0.5 <= keyword_density <= 3.0,
        "meta_description": meta_desc,
        "meta_description_length": meta_desc_length,
        "meta_description_pass": 150 <= meta_desc_length <= 160 and meta_desc_has_keyword,
    }


def ai_checks(markdown: str, keyword: str, author_context: str = "") -> dict:
    """
    LLM-as-Judge scoring across 13 dimensions.
    Follows Google's agent pattern: Observe (read article) → Reason (think privately)
    → Act (score each dimension with reasoning grounded in the actual content).
    """
    context_line = f"\nAuthor context: {author_context}" if author_context else ""
    prompt = f"""You are a senior content strategist and SEO editor with 15 years of experience publishing articles that rank on page one of Google AND get cited by AI search engines like ChatGPT, Gemini, Claude, and Perplexity. You understand both traditional SEO and AEO (Answer Engine Optimization).

Your job is to score the article below using Google's E-E-A-T framework (Experience, Expertise, Authoritativeness, Trustworthiness) combined with AEO signals — what makes content get cited by AI systems.

Key principle from Google's AI search guidelines: "First-hand reviews and original analysis outperform commodity summaries." A founder or practitioner writing from lived experience has legitimate E-E-A-T through Experience. Personal testimony and firsthand observation count as valid authority — weigh this accordingly if author context is provided.
{context_line}
Target keyword: "{keyword}"

Before scoring, think through these questions privately (do not include this in your output):
- Who is the likely reader and what do they actually need?
- Does this article have a unique perspective an AI would want to cite, or does it duplicate what's already everywhere?
- What would a truly great article on this topic look like — specific, experienced, insightful?
- Where does this article fall short of that standard?

Then score on all 13 dimensions. Be critical and honest. Most articles are average (5-6). A 9-10 should be rare and earned. Do NOT default to 7 for everything — that is the most common failure mode.

Article:
{markdown[:6000]}

Hard constraints:
- If the intro starts with "In today's..." or a generic observation, intro_strength is max 4.
- If no real sources are cited AND no firsthand experience is present, source_quality is max 3.
- If the article could have been written by someone with zero firsthand experience, originality is max 5.
- If there is no clear next step for the reader, cta_strength is max 4.
- For ai_citability: look for specific quotable sentences, direct answers, concrete data points that an AI could extract verbatim. Vague conclusions score 1-3.

Return ONLY valid JSON in this exact format:
{{
  "search_intent_match": {{
    "score": <1-10>,
    "reasoning": "<one sentence — does this article match what someone searching this keyword actually wants?>"
  }},
  "goal_achievement": {{
    "score": <1-10>,
    "reasoning": "<one sentence — does the article fully deliver on its stated title/promise?>"
  }},
  "content_depth": {{
    "score": <1-10>,
    "reasoning": "<one sentence — does it go beyond surface-level? Does it cover subtopics thoroughly or just skim them?>"
  }},
  "audience_fit": {{
    "score": <1-10>,
    "reasoning": "<one sentence — is the tone, vocabulary, and complexity right for the likely target audience?>"
  }},
  "intro_strength": {{
    "score": <1-10>,
    "reasoning": "<one sentence — does the opening hook the reader in the first 2-3 sentences or does it waste their time?>"
  }},
  "originality": {{
    "score": <1-10>,
    "reasoning": "<one sentence — 10 = expert voice, unique data, surprising insight; 1 = generic AI filler with no original thought>"
  }},
  "insightfulness": {{
    "score": <1-10>,
    "reasoning": "<one sentence — does it offer at least one insight the reader couldn't get from the first 5 Google results?>"
  }},
  "cta_strength": {{
    "score": <1-10>,
    "reasoning": "<one sentence — is there a clear compelling next step for the reader, or does the article just end?>"
  }},
  "factual_accuracy": {{
    "score": <1-10>,
    "reasoning": "<one sentence — are facts, stats, and claims specific, accurate, and verifiable?>"
  }},
  "source_quality": {{
    "score": <1-10>,
    "reasoning": "<one sentence — are sources cited or does firsthand experience provide authority?>"
  }},
  "readability": {{
    "score": <1-10>,
    "reasoning": "<one sentence — is it scannable, well-structured, and written in plain clear language?>"
  }},
  "hallucination_risk": {{
    "score": <1-10>,
    "reasoning": "<one sentence — 10 = every claim is grounded or cited; 1 = multiple fabricated or unverifiable statements>"
  }},
  "ai_citability": {{
    "score": <1-10>,
    "reasoning": "<one sentence — does the article contain specific, quotable sentences or direct answers that ChatGPT, Gemini, or Perplexity could extract and cite verbatim?>"
  }}
}}"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"No JSON object found in response: {raw[:200]}")
    return json.loads(raw[start:end])


def generate_revision_instructions(
    markdown: str,
    keyword: str,
    failing_dimensions: list[str],
    ai_scores: dict,
    author_context: str = "",
) -> list[str]:
    """
    For each failing dimension, generate one specific, actionable instruction
    the writing pipeline can use to fix the article on the next pass.
    Follows Google's agent principle: every FAIL must have a path to PASS.
    """
    if not failing_dimensions:
        return []

    failing_summary = "\n".join(
        f"- {dim} (score {ai_scores[dim]['score']}/10): {ai_scores[dim]['reasoning']}"
        for dim in failing_dimensions
    )
    context_line = f"\nAuthor context: {author_context}" if author_context else ""

    prompt = f"""You are an expert content editor. An SEO article has been scored and is failing on the dimensions listed below. Your job is to write ONE specific, actionable revision instruction for each failing dimension.

Rules for each instruction:
- Be concrete. Don't say "improve this." Say exactly what to add, change, or remove.
- Give an example where helpful (e.g. "Instead of X, write Y" or "Add a sentence like: '...'").
- If the author has firsthand experience, tell them to use it — that's their strongest asset.
- Each instruction should be executable by a writer in under 10 minutes.
{context_line}
Target keyword: "{keyword}"

Article opening (first 1500 chars for context):
{markdown[:1500]}

Failing dimensions:
{failing_summary}

Return ONLY a JSON array of strings — one instruction per failing dimension, in the same order:
["<instruction for dimension 1>", "<instruction for dimension 2>", ...]"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    start = raw.find("[")
    end = raw.rfind("]") + 1
    if start == -1 or end == 0:
        return [f"Improve: {dim}" for dim in failing_dimensions]
    return json.loads(raw[start:end])


def score_article(
    markdown_path: str,
    keyword: str,
    author_context: str = "",
    attempt: int = 1,
) -> dict:
    """
    Full eval pipeline following the Google agent loop:
    1. Observe  — read article, detect missing context
    2. Reason   — score all dimensions (code-based + LLM-as-Judge)
    3. Act      — compute verdict, generate revision instructions if failing
    4. Notify   — surface what the pipeline or user needs to provide
    """
    markdown = Path(markdown_path).read_text(encoding="utf-8")

    # Step 1: Observe — detect missing context before scoring
    needs_context = _check_missing_context(markdown, keyword, author_context)

    # Step 2a: Code-based graders (deterministic, no LLM)
    mechanical = mechanical_checks(markdown, keyword)

    # Step 2b: Model-based graders (LLM-as-Judge)
    ai = ai_checks(markdown, keyword, author_context)

    # Step 3: Compute verdict
    ai_average = round(sum(v["score"] for v in ai.values()) / len(ai), 1)

    mechanical_passes = sum([
        mechanical["word_count_pass"],
        mechanical["heading_structure_pass"],
        mechanical["keyword_density_pass"],
        mechanical["meta_description_pass"],
    ])

    hallucination_score = ai["hallucination_risk"]["score"]
    overall_pass = (
        ai_average >= AI_PASS_THRESHOLD
        and mechanical_passes >= MECHANICAL_PASS_REQUIRED
        and hallucination_score >= HALLUCINATION_PASS_THRESHOLD
    )

    # Step 4a: Identify failing dimensions (score below threshold)
    failing_dimensions = [
        dim for dim, result in ai.items()
        if result["score"] < FAIL_THRESHOLD
    ]

    # Step 4b: Generate revision instructions for failing dimensions
    # (second focused AI call — only runs when there's something to fix)
    revision_instructions = {}
    if not overall_pass and failing_dimensions:
        instructions = generate_revision_instructions(
            markdown, keyword, failing_dimensions, ai, author_context
        )
        revision_instructions = dict(zip(failing_dimensions, instructions))

    result = {
        "file": markdown_path,
        "keyword": keyword,
        "attempt": attempt,
        "mechanical": mechanical,
        "ai_scores": ai,
        "ai_average": ai_average,
        "mechanical_passes": f"{mechanical_passes}/4",
        "hallucination_score": hallucination_score,
        "overall_pass": overall_pass,
        "verdict": "PASS" if overall_pass else "FAIL",
    }

    if not overall_pass:
        result["failing_dimensions"] = failing_dimensions
        result["revision_instructions"] = revision_instructions

    # Always surface context notifications so the pipeline/user can act on them
    if needs_context:
        result["needs_context"] = needs_context

    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python scorer.py <markdown_file> <keyword> [author_context]")
        sys.exit(1)

    author_context = sys.argv[3] if len(sys.argv) > 3 else ""
    result = score_article(sys.argv[1], sys.argv[2], author_context)
    print(json.dumps(result, indent=2))
