# seoclaw — project plan & roadmap

> Planning doc for the team. User-facing docs live in [README.md](README.md).


SEO Claw can:
- Do research on your behalf to come up with a content strategy
- Monitor your competitors to make sure you don't get left behind
- Write and review content on your behalf
- Monitor the internet for customers facing problems your company could solve

## Project Breakdown
### SEO Agent
#### Core SEO Agent (Ben)
> Goal: Proactive agent that acts like an SEO teammate, reaching out with reports + writing content.

This is the core loop that will result in content for your website:
- Understand your website's positioning and current SEO performance
- Research keywords that would drive valuable traffic to your page
- Research what your competitors top pages are so you can target the same keywords
- Come up with a content plan
- Write and review content
- Refresh underperforming or out of data content

#### Social Listening (Nick)
> Goal: Identify relevant comment / posts on social media so that the company can engage with them.

- Ask the user for what kind of content they're interested in being notified about.
- Set up monitors for those terms
- Filter down the identified posts based on whether they would actually be something the user would be interested in given what they've told the agent about their company.
- Send a report with X posts relevant towards the user on the cadence that they request.

### Content Eval Suite (Nick)
> Goal: Build an eval suite so that we confidently improve our writing pipeline and identify regressions

> Non Goal: Build the content pipeline to write better AI posts. This will be handled by the core SEO agent. 

- Identify quality content from reputable websites to be treated as "good content". 
- Ask claude to create content for similar topics. This will be treated as "bad content" since it will be default AI output that hasn't gone though our pipeline.
- Create a rubric which correctly identifies good versus bad content:
  - Is the introduction strong?
  - Does the article achieve its goal in an interesting, helpful or persuasive way?
  - Is there a clear call to action or outcome for the user which feels natural?
  - Is the writing style pleasant? Does it read like "AI slop"?
    - Tip: Look at ai skills for "deslop-ing" ai writing to see common phrases.
  - Are there any baseless, non-cited claims?
- promptfoo could be a good eval tool? I haven't built one of these in a while.
  - https://www.promptfoo.dev/docs/getting-started/
