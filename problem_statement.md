

## Problem Statement
Product teams need a fast, evidence-backed way to understand why quick-commerce users keep repeating the same purchases and what prevents them from trying new categories.

Customer feedback relevant to this exists across App Store reviews, Play Store reviews, Reddit, forums, and other public discussions — but it's noisy, repetitive, and often dominated by delivery complaints or app bugs, which buries the real behavior patterns underneath. As a result, teams spend too much time manually reading feedback and still walk into interviews with hypotheses shaped by bias and anecdote, not evidence.

**How might we help Product Managers automatically surface, organize, and prioritize evidence-backed customer insights from this feedback — before they design interviews, not after?**

## Approach (the response to the problem, not the problem itself)
An AI-powered workflow that mines this feedback, clusters it into themes, and scores each theme so a PM can tell which ones are actually worth spending an interview slot on.

## What the Engine Should Answer
* Why users repeat the same purchases
* What blocks exploration of new categories
* How users discover products today
* **What information users look for before trying a category they've never bought** *(restored)*
* What role habit plays in purchase behavior
* What frustrations, unmet needs, or hesitation patterns recur
* Which segments seem more open to experimentation
* Which themes deserve follow-up in interviews

## Output Schema
Theme · Example quotes · Frequency/prevalence · Sources · Sentiment · Signal strength · Suggested insight · Suggested research question

## Scoring Logic
**Prevalence** — how many users mention it, how widely it appears across the dataset.
**Signal strength** — same mechanism across multiple sources, specific language rather than vague, consistent enough to trust. *(If sentiment is inconsistent within a theme, treat that as a cue the theme is bundling two mechanisms — re-cluster it, don't just score it lower.)*

## Prioritization Rule *(new — this is what was missing)*
* **Medium/High on both** → promote to Suggested Research Question. This is what your 5–6 interviews test.
* **High prevalence, low signal strength** → "Monitor" — loud but vague or single-source. Don't spend an interview slot yet.
* **Low prevalence, high signal strength** → "Niche but credible" — worth naming in the deck, not worth a scarce slot this round.
* **Low on both** → drop from the shortlist.

## Purpose
Not to prove one pre-decided hypothesis. To find the strongest patterns using prevalence and signal strength together — then let interviews validate, refine, or reject them.

## Success Looks Like
A short list (roughly 3–6 themes, sized to match your actual interview capacity) of evidence-backed hypotheses, each carrying a specific research question, ready to feed directly into the screener you already built.

