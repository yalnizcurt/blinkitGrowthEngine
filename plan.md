# Implementation Plan: Quick-Commerce Insight Engine

## Overview

Build a Python-based pipeline that **collects** public customer feedback about Blinkit (and optionally Zepto/Instamart), **clusters** it into behavioral themes using NLP, **scores** each theme on prevalence + signal strength, and **outputs** a prioritized shortlist of 3–6 research-ready hypotheses with suggested interview questions.

---

## Phase 1 — Data Collection

### Step 1: Play Store Reviews
- Use the `google-play-scraper` Python library
- Package name: `com.grofers.customerapp`
- Pull **all available reviews** (aim for 5,000–10,000+), capturing: review text, rating, date, thumbs-up count
- Filter to English-language reviews (or translate Hindi reviews with an LLM pass)

### Step 2: App Store Reviews
- Use the `app-store-scraper` Python library
- App ID: `1456032724`
- Same fields: review text, rating, date

### Step 3: Reddit Discussions
- Use **PRAW** (Python Reddit API Wrapper) with a Reddit developer app (script type)
- Target subreddits: `r/india`, `r/indiasocial`, `r/IndianStreetBets`, `r/bangalore`, `r/delhi`, `r/mumbai`, `r/StartUpIndia`
- Search queries: `"blinkit"`, `"quick commerce"`, `"10 minute delivery"`, `"zepto"`, `"instamart"`, `"grocery delivery app"`
- Collect both **posts and comments** — comments often contain the richest behavioral detail
- Capture: text, score (upvotes), subreddit, timestamp, parent post title

### Step 4: Normalize into a Unified Dataset
- Create a single DataFrame/CSV with columns:
  - `id`, `source` (play_store / app_store / reddit), `text`, `rating` (if applicable), `date`, `upvotes` (if applicable), `url`
- **De-duplicate** by fuzzy text matching (>90% similarity → drop)
- Store raw + cleaned versions

### Step 5: Pre-filter Noise
- Use an LLM (Gemini Flash) or keyword classifier to **tag and exclude** reviews that are purely about:
  - Delivery logistics complaints (late delivery, wrong item)
  - App crashes / bugs / UI glitches
  - Payment failures
  - Generic praise ("great app 5 stars")
- Keep anything that touches **purchase behavior, product discovery, habits, category exploration, or hesitation**
- Tag borderline reviews as "uncertain" rather than dropping them

---

## Phase 2 — Embedding & Clustering

### Step 6: Generate Embeddings
- Use `sentence-transformers` with a model like `all-MiniLM-L6-v2` (fast, good for short text) or `all-mpnet-base-v2` (better quality)
- Embed every cleaned feedback entry into a dense vector

### Step 7: Cluster with BERTopic
- Pipeline: **Sentence Embeddings → UMAP (dimensionality reduction) → HDBSCAN (clustering) → c-TF-IDF (topic representation)**
- Key config:
  - `min_topic_size=15` (avoid micro-clusters)
  - `nr_topics="auto"` initially, then manually merge if >20 topics
  - HDBSCAN will automatically assign noisy/unclassifiable reviews to topic `-1` — review these later
- This should yield ~10–25 raw clusters

### Step 8: Label Clusters with an LLM
- For each cluster, take the top-20 representative documents + c-TF-IDF keywords
- Send to Gemini (or GPT-4) with a prompt like:
  > "These are customer feedback snippets from a quick-commerce app. They've been grouped by semantic similarity. Give this cluster a short, descriptive behavioral theme name (e.g., 'Habitual reordering of staples', 'Distrust of produce quality in new categories'). Also provide a 1-sentence description of the underlying user mechanism."
- Store: `cluster_id`, `theme_name`, `mechanism_description`, `keywords`

### Step 9: Validate & Merge Clusters
- Manually review the ~10–25 clusters:
  - Merge clusters that describe the same mechanism from different angles
  - Split clusters where sentiment is **inconsistent** within the theme (per the problem statement: "re-cluster it, don't just score it lower")
- Target: **8–15 clean themes**

---

## Phase 3 — Scoring & Prioritization

### Step 10: Compute Prevalence Score (per theme)
- **Count**: number of unique feedback entries in the cluster
- **Breadth**: number of distinct sources (Play Store, App Store, Reddit) the theme appears in
- **Normalize** to a 1–5 scale relative to dataset size:
  - 5 = top 10% by count + appears in 3/3 sources
  - 1 = bottom 20% by count + single source

### Step 11: Compute Signal Strength Score (per theme)
- Use an LLM to evaluate each cluster on:
  - **Specificity**: Are users describing a concrete mechanism/behavior, or vague complaints? (score 1–5)
  - **Consistency**: Do the reviews within the cluster describe the **same** underlying dynamic? (score 1–5)
  - **Cross-source corroboration**: Does the same pattern appear independently across sources? (score 1–5)
- Average → Signal Strength score (1–5)

### Step 12: Sentiment Analysis (per theme)
- Use Gemini structured output to classify each review as: `positive`, `negative`, `neutral`, `mixed`
- Aggregate per cluster → dominant sentiment + distribution
- Flag clusters with **bimodal sentiment** for potential re-splitting

### Step 13: Apply Prioritization Matrix
Using the rules from the problem statement:

| Prevalence | Signal Strength | Action |
|---|---|---|
| Medium/High | Medium/High | **→ Promote to Suggested Research Question** |
| High | Low | **→ "Monitor"** — loud but vague |
| Low | High | **→ "Niche but credible"** — name in deck |
| Low | Low | **→ Drop** from shortlist |

- Target output: **3–6 promoted themes** (sized to interview capacity)

---

## Phase 4 — Output Generation

### Step 14: Build the Output Schema
For each theme, generate a structured record:

```json
{
  "theme": "Habitual reordering limits category exploration",
  "example_quotes": ["quote1", "quote2", "quote3"],
  "frequency": 342,
  "prevalence_score": 4,
  "sources": ["play_store", "reddit", "app_store"],
  "sentiment": "mixed (60% negative, 30% neutral, 10% positive)",
  "signal_strength_score": 4,
  "priority": "Promote to Research Question",
  "suggested_insight": "Users develop muscle-memory reorder flows that actively discourage browsing. The reorder UX itself may be a barrier to category expansion.",
  "suggested_research_question": "Walk me through your last 3 orders — at what point did you consider buying something you hadn't bought before, and what happened?"
}
```

### Step 15: Generate the Research Questions
- For each promoted theme, use an LLM to generate:
  - A **suggested insight** (1-sentence hypothesis)
  - A **suggested research question** (open-ended, suitable for a 30-min user interview)
  - A **screener criteria suggestion** (what kind of user to recruit for this question)

### Step 16: Export & Presentation
- Export as:
  - **JSON** (for programmatic use)
  - **CSV/Excel** (for PM consumption)
  - **Markdown report** (for sharing in docs/Notion)
- Include a summary dashboard section with:
  - Total feedback analyzed, by source
  - Theme distribution chart
  - Prioritization matrix visualization (2×2 grid)

---

## Phase 5 — Verification & Iteration

### Step 17: Sanity Checks
- Spot-check 10 random reviews per cluster — do they actually belong?
- Verify that the 3–6 promoted themes genuinely map to the "What the Engine Should Answer" questions from the problem statement
- Confirm no high-signal feedback was lost to the noise filter in Step 5

### Step 18: Sensitivity Testing
- Re-run clustering with different `min_topic_size` values (10, 15, 25) to see if themes are stable
- Check if the prioritization ranking changes meaningfully — stable rankings = trustworthy output

---

## Tech Stack Summary

| Layer | Tool |
|---|---|
| Language | Python 3.11+ |
| Play Store scraping | `google-play-scraper` |
| App Store scraping | `app-store-scraper` |
| Reddit scraping | `PRAW` |
| Embeddings | `sentence-transformers` |
| Clustering | `BERTopic` (UMAP + HDBSCAN + c-TF-IDF) |
| LLM (labeling, scoring, questions) | Gemini 2.0 Flash via `google-genai` SDK |
| Sentiment | Gemini structured output (Pydantic schema) |
| Data handling | `pandas` |
| Output | JSON, CSV, Markdown |

---

## File Structure (Proposed)

```
blinkit/
├── problem_statement.md
├── config.py                  # API keys, app IDs, scraper settings
├── requirements.txt
├── main.py                    # Orchestrator — runs the full pipeline
│
├── collectors/
│   ├── __init__.py
│   ├── playstore.py           # google-play-scraper wrapper
│   ├── appstore.py            # app-store-scraper wrapper
│   ├── reddit.py              # PRAW-based collector
│   └── normalizer.py          # Merge all sources → unified DataFrame
│
├── preprocessing/
│   ├── __init__.py
│   ├── cleaner.py             # Text cleaning, dedup, language filter
│   └── noise_filter.py        # LLM-based relevance filtering (drop logistics/bugs)
│
├── analysis/
│   ├── __init__.py
│   ├── embeddings.py          # Sentence-transformer embedding generation
│   ├── clustering.py          # BERTopic pipeline + cluster merging
│   ├── labeler.py             # LLM-based cluster labeling
│   ├── scorer.py              # Prevalence + signal strength computation
│   └── sentiment.py           # Per-review + per-cluster sentiment
│
├── output/
│   ├── __init__.py
│   ├── schema.py              # Pydantic models for the output schema
│   ├── question_generator.py  # LLM generates insights + research questions
│   └── exporter.py            # JSON / CSV / Markdown report generation
│
├── data/
│   ├── raw/                   # Raw scraped data (gitignored)
│   ├── cleaned/               # Post-dedup, post-filter
│   └── results/               # Final outputs
│
└── notebooks/
    └── exploration.ipynb      # Ad-hoc analysis, cluster visualization
```

---

## Execution Order (Pipeline)

```
1. collectors/playstore.py    ─┐
2. collectors/appstore.py     ─┼─→ collectors/normalizer.py → unified.csv
3. collectors/reddit.py       ─┘
4. preprocessing/cleaner.py        → cleaned.csv
5. preprocessing/noise_filter.py   → filtered.csv (behavioral feedback only)
6. analysis/embeddings.py          → embeddings.npy
7. analysis/clustering.py          → clusters.csv (review → cluster mapping)
8. analysis/labeler.py             → themes.json (cluster labels + descriptions)
9. analysis/sentiment.py           → sentiment.csv (per-review sentiment)
10. analysis/scorer.py             → scored_themes.json (prevalence + signal strength)
11. output/question_generator.py   → research_questions.json
12. output/exporter.py             → final report (JSON + CSV + Markdown)
```

---

## Estimated Effort

| Phase | Work | Time Estimate |
|---|---|---|
| Phase 1 — Data Collection | Scrapers + normalization + noise filter | ~4–5 hours |
| Phase 2 — Clustering | Embeddings + BERTopic + LLM labeling | ~3–4 hours |
| Phase 3 — Scoring | Prevalence + signal strength + sentiment + prioritization | ~2–3 hours |
| Phase 4 — Output | Schema + question generation + export | ~2–3 hours |
| Phase 5 — Verification | Spot checks + sensitivity testing | ~1–2 hours |
| **Total** | | **~12–17 hours** |

---

## Key Decisions / Open Questions

1. **Gemini API key** — Do you already have a Google AI Studio / Vertex AI API key, or should I use a free-tier setup? - Will use GrokAPI Keys

2. **Reddit API credentials** — Do you have a Reddit developer app set up, or should I include instructions for creating one? (It's free, takes ~2 minutes.) - Will use Scrapegraph for Reddit API (Dont have reddit API)

3. **Competitor data** — Should the pipeline also scrape Zepto (`com.zuzu.zeptoconsumerapp`) and Swiggy Instamart alongside Blinkit to compare behavioral patterns, or keep it Blinkit-only? - Let's keep it Blinkit only for now

4. **Scale** — Are you okay with ~5K–10K reviews as the dataset, or do you want to go larger (which may require managed scraping APIs like SerpApi)? - 5K reviews should be good

5. **Output format preference** — The plan includes JSON + CSV + Markdown. Do you have a preference for a primary format, or a tool you'd import into (Notion, Google Sheets, Airtable)?     - CSV preferred

6. **Interview screener integration** — The problem statement mentions "feed directly into the screener you already built." Do you have an existing screener I should design the output to plug into? - No, Dont have an existing screener

