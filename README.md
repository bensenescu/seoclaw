# seoclaw

SEO content evaluation suite built for the ZeroClaw harness. Automatically grades articles before they publish using code-based checks and an LLM-as-Judge, following Google's E-E-A-T framework and AEO (Answer Engine Optimization) signals for AI search engines like ChatGPT, Gemini, and Perplexity.

## What it does

Ben's pipeline generates SEO articles. Before an article ships, `scorer.py` grades it across 13 dimensions and returns a PASS or FAIL with specific revision instructions. If it fails, the pipeline revises and re-scores until it passes.

```
Article draft → scorer.py → PASS → publish
                          → FAIL → revision_instructions → rewrite → score again
```

## Eval dimensions (13 total)

**Code-based (deterministic):**
- Word count ≥ 800
- Heading structure (1 H1, ≥ 2 H2s)
- Keyword density 0.5–3%
- Meta description present, 150–160 chars, contains keyword

**LLM-as-Judge (Claude Haiku):**
- Search intent match
- Goal achievement
- Content depth
- Audience fit
- Intro strength
- Originality (detects AI slop)
- Insightfulness
- CTA strength
- Factual accuracy
- Source quality
- Readability
- Hallucination risk
- AI citability (for ChatGPT / Gemini / Perplexity)

## Setup

```bash
cp .env.example .env
# Add your Anthropic API key to .env
```

## Run

```bash
python eval/scorer.py <article.md> "<target keyword>" "[optional: author context]"
```

Example:
```bash
python eval/scorer.py eval/sample_article.md "keyword research"
python eval/scorer.py eval/sample_article.md "keyword research" "Startup founder with 5 years in fashion SEO"
```

## Output

```json
{
  "verdict": "PASS" | "FAIL",
  "ai_average": 7.4,
  "mechanical_passes": "4/4",
  "failing_dimensions": ["cta_strength", "originality"],
  "revision_instructions": {
    "cta_strength": "End with one concrete action...",
    "originality": "Add a section from your firsthand experience..."
  },
  "needs_context": ["CONTEXT NEEDED — No author context provided..."]
}
```

## Integration

Ben's ZeroClaw pipeline calls `score_article()` directly:

```python
from eval.scorer import score_article

result = score_article(
    markdown_path="draft.md",
    keyword="target keyword",
    author_context="founder, fashion industry",
    attempt=1,
)

if result["verdict"] == "PASS":
    publish(result["file"])
else:
    revise(result["revision_instructions"], attempt=result["attempt"] + 1)
```

## License

Apache 2.0
