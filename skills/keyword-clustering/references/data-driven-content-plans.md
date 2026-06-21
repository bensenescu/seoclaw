# Data-driven content plans with OpenSEO MCP

Use this reference when updating a durable content plan from live OpenSEO data.

## Required context before scoring pages

Capture the business strategy in the plan, not just keywords:

- Primary conversion goal, e.g. organic traffic that becomes paid subscribers.
- Secondary demand goal, e.g. open-source repo visibility/community demand.
- Current audience and later audience.
- Language and market.
- Strategic assets that should receive demand, such as a GitHub repo, docs, free tool, or comparison page.

These inputs change prioritization. A lower-volume, high-fit product/MCP/open-source query can outrank a higher-volume generic education query if it better supports conversion or strategic demand.

## Live data sources to pull

Prefer OpenSEO MCP over manual exports:

1. `whoami` and `list_projects` to verify connection and pick the project.
2. Search Console `dimensions: ['query','page']` for query-to-URL mapping, striking-distance terms, and cannibalization.
3. Search Console `dimensions: ['page']` for current URL demand, CTR, and average position.
4. `list_saved_keywords` for existing tags/clusters.
5. `get_keyword_metrics` for volume, KD, CPC, intent, and trend data on candidate terms.
6. `get_serp_results` for representative queries to validate page type and SERP format.
7. `find_serp_competitors` for cross-query competitor patterns when market leadership matters.

## Prioritization pattern

Rank work in this order unless the data strongly says otherwise:

1. Existing pages with Search Console impressions and clear paid-conversion intent.
2. Existing pages or assets that support a strategic demand goal, such as open-source repo visibility.
3. Existing pages that can bridge the stated audience into product usage, such as founder/DIY SEO guides.
4. Net-new pages for proven saved clusters or live SERP opportunities.
5. Generic high-volume education topics only when they can be made product-led or support a later cluster.

## Output expectations

A good plan should include:

- MCP/data status and project used.
- Business goals and audience assumptions.
- Current Search Console baseline by page and important query.
- Keyword metrics table with volume/KD/CPC/intent.
- SERP and competitor read.
- P0/P1/P2 roadmap with page-level briefs.
- Internal-link plan, including links to strategic assets like GitHub repos.
- Measurement plan tied to starting impressions/positions and conversion actions.

## Pitfalls

- Do not treat volume as the strategy. Paid-conversion fit and strategic visibility can matter more.
- Do not ask for GSC CSV exports when OpenSEO MCP has Search Console access.
- Do not bury user-supplied business goals in the intro only; use them to reorder priorities.
- Do not recommend generic GEO/AEO or broad SEO education pages ahead of more defensible product-led pages unless the user explicitly wants awareness over conversion.
