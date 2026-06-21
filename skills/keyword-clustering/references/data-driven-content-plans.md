# Data-driven OpenSEO content plans

Use this reference when a user asks for a content plan, SEO roadmap, or content-priority update and OpenSEO MCP data is available.

## Data sources to combine

- `whoami` + `list_projects`: prove MCP connectivity and choose the correct project/domain.
- GSC `dimensions: ['query','page']`: query-to-URL mapping, striking-distance opportunities, accidental cannibalization, and pages receiving impressions for the wrong intent.
- GSC `dimensions: ['page']`: page-level demand, CTR, and average-position baseline.
- `list_saved_keywords`: existing cluster/tag strategy; do not duplicate saved work.
- `get_keyword_metrics`: volume, KD, CPC, intent, and trend for the candidate cluster heads.
- `get_serp_results`: validate SERP intent and page format for representative terms.
- `find_serp_competitors`: identify recurring market winners and domain types across the planned query set.

## Analysis pattern

1. Normalize GSC query+page rows into:
   - top non-brand queries by impressions,
   - striking-distance terms, e.g. avg position 4-30 with meaningful impressions,
   - page aggregates with top queries per page.
2. Compare GSC terms with saved keyword tags/clusters. Saved tags are planning context, not proof of current rankings.
3. Hydrate only the candidate cluster heads with keyword metrics; avoid spending credits on every long-tail variant unless the user asks for exhaustive research.
4. Use live SERPs for page-type decisions:
   - product/tool pages vs guides/listicles vs directories/forums,
   - AI Overview or PAA presence,
   - authority gap and competitor type.
5. Prioritize existing page updates when GSC already shows impressions, then propose net-new pages for uncovered intent.
6. Defer tempting high-volume clusters when KD/authority gap or intent mismatch makes them weaker than lower-volume product-led terms.

## Recommended deliverable structure

- MCP/project/data status and date range.
- Executive strategy in 2-4 bullets.
- Current organic baseline from domain overview and GSC pages.
- Striking-distance and high-impression query tables.
- SERP/competitor read with domain types.
- Prioritized content plan:
  - P0 existing URL updates,
  - P1 net-new pages,
  - P2 deferred/support-only topics.
- 6-8 week execution roadmap.
- Measurement plan with starting GSC baseline and target movement.
- Internal linking plan with exact/near-exact anchors.
- Saved keyword tags/clusters to preserve.
- “What not to do yet” to keep the strategy focused.

## File-writing convention

If the user asks to update the plan and no existing plan file is found, create `seo/<domain>/content-plan.md` in the repo or SEO workspace. Include enough source metrics that a future session can audit why priorities were chosen without re-running every paid query immediately.
