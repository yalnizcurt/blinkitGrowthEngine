"""
Rigorous behavioral theme extraction from filtered reviews.
This script classifies every substantive review into behavioral categories
using keyword patterns + manual heuristic rules, NOT automated clustering.
"""
import csv
import re
import json
from collections import Counter, defaultdict

# Load data
with open('data/cleaned/filtered_reviews.csv', 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Only analyze reviews with enough text to carry meaning
substantive = [r for r in rows if len(r.get('cleaned_text','')) > 40]
print(f"Total reviews: {len(rows)}")
print(f"Substantive reviews (>40 chars): {len(substantive)}")
print(f"Short noise discarded: {len(rows) - len(substantive)}")
print()

# ---- CLASSIFICATION RULES ----
# Each rule: (theme_id, theme_label, classification, patterns_list)
# classification: behavioral | operational | generic | mixed

RULES = [
    # BEHAVIORAL THEMES - category adoption / repeat purchase / trial barriers
    ("B1", "Price premium awareness vs convenience tradeoff",
     "behavioral",
     [r"(?:price|prices|expensive|costly|overpriced|higher than|more than|mrp|markup|premium).{0,60}(?:market|store|shop|retail|bigbasket|dmart|amazon|flipkart|local|outside|offline)",
      r"(?:market|store|shop|retail|local|outside|offline).{0,60}(?:cheap|cheaper|less|lower|affordable)",
      r"(?:price|prices|expensive|costly).{0,40}(?:but|still|however|though).{0,40}(?:convenient|fast|quick|time|save)",
      r"(?:save|saves|saving).{0,30}(?:time|effort).{0,30}(?:but|though|however).{0,30}(?:price|expensive|cost)",
      r"higher than (?:the )?mrp",
      r"prices? (?:are |is )?(?:too |very |quite )?(?:high|expensive|costly|inflated)"]),

    ("B2", "Quality/freshness uncertainty prevents non-grocery trial",
     "behavioral",
     [r"(?:fresh|freshness|quality|rotten|spoil|expire|stale|damage|defective|broken).{0,60}(?:vegetable|fruit|produce|grocery|food|meat|fish|chicken|egg|milk|dairy|bread|batter)",
      r"(?:vegetable|fruit|produce|grocery|food).{0,60}(?:rotten|spoil|expire|stale|bad|worst|poor quality)",
      r"(?:quality|condition).{0,40}(?:not good|bad|poor|worst|terrible|horrible|disgusting)",
      r"(?:rotten|spoiled|expired|stale|damaged|defective|broken).{0,30}(?:product|item|thing|stuff)"]),

    ("B3", "Return/refund policy as barrier to trying non-grocery categories",
     "behavioral",
     [r"(?:return|refund|exchange|replace|money back).{0,60}(?:not|no|won't|can't|cannot|denied|refuse|reject|difficult|worst|bad|policy)",
      r"(?:no|not|won't|can't|cannot).{0,30}(?:return|refund|exchange|replace)",
      r"return policy.{0,30}(?:bad|worst|poor|terrible|no|not)",
      r"(?:bought|ordered|purchased).{0,60}(?:defective|broken|wrong|damaged).{0,60}(?:no|not|won't|can't).{0,30}(?:return|refund|exchange)"]),

    ("B4", "Competitive comparison driving category switching",
     "behavioral",
     [r"(?:flipkart|amazon|bigbasket|dmart|zepto|instamart|swiggy|jiomart|dunzo).{0,60}(?:better|cheaper|good|best|prefer|switch|use|moved|shift)",
      r"(?:better|cheaper|good|prefer).{0,40}(?:flipkart|amazon|bigbasket|dmart|zepto|instamart|swiggy|jiomart)",
      r"(?:switch|shifted|moved|going).{0,30}(?:to|from).{0,20}(?:flipkart|amazon|bigbasket|dmart|zepto|instamart|swiggy)"]),

    ("B5", "Convenience-driven habitual repeat purchase",
     "behavioral",
     [r"(?:every|daily|always|regular|habit|routine|always order|keep ordering|go-to|goto|rely on|depend).{0,40}(?:blinkit|order|use|app|buy|purchase|grocery|essential)",
      r"(?:essential|urgent|emergency|immediate|instant|last.minute|quick need).{0,40}(?:order|buy|use|app|blinkit)",
      r"(?:blinkit|app).{0,40}(?:go.to|first choice|my favorite|prefer|always use|daily use)"]),

    ("B6", "Assortment gaps limiting category exploration",
     "behavioral",
     [r"(?:not available|unavailable|out of stock|no stock|limited|don't have|doesn't have|can't find|couldn't find).{0,40}(?:product|item|brand|option|variety|category|selection)",
      r"(?:product|item|brand|option|variety|selection|range|assortment).{0,40}(?:limited|less|few|not enough|missing|not available|unavailable)",
      r"(?:add|include|bring|want|need|wish).{0,30}(?:more|new|other|different).{0,30}(?:product|item|brand|category|option)"]),

    ("B7", "Fee/surcharge sensitivity blocking small/trial orders",
     "behavioral",
     [r"(?:delivery (?:charge|fee|cost)|platform fee|handling fee|surcharge|packing|extra charge|minimum order).{0,60}(?:high|too|very|expensive|increased|ridiculous|absurd|unreasonable)",
      r"(?:fee|charge|cost).{0,30}(?:increased|hiked|raised|doubled|too much|very high|ridiculous)",
      r"(?:minimum order|min order|cart value).{0,40}(?:high|too|increased|₹|rs)"]),

    ("B8", "Product description/image mismatch reducing trust for new categories",
     "behavioral",
     [r"(?:description|image|photo|picture|display|shown|advertised).{0,40}(?:different|wrong|misleading|fake|not same|not matching|mismatch|doesn't match)",
      r"(?:received|got|delivered).{0,40}(?:different|wrong|not same|not what).{0,30}(?:order|expected|shown|display)",
      r"(?:wrong|different|smaller|less|inferior).{0,30}(?:product|item|size|quantity|variant).{0,30}(?:than|from).{0,20}(?:shown|display|image|order|expected)"]),

    ("B9", "Medicine/pharmacy category positive discovery",
     "behavioral",
     [r"(?:medicine|pharmacy|medical|pharma|tablet|capsule|health).{0,40}(?:delivery|available|order|get|buy|fast|quick|great|good|amazing|useful|helpful|lifesaver)",
      r"(?:delivery|available|order).{0,30}(?:medicine|pharmacy|medical)"]),

    ("B10", "Non-grocery electronics/lifestyle trial and disappointment",
     "behavioral",
     [r"(?:bluetooth|earphone|headphone|charger|cable|electronic|gadget|phone|mobile|accessory|toy).{0,60}(?:not working|broken|defective|cheap|worst|bad|fake|duplicate|poor quality|waste)",
      r"(?:bought|ordered|tried).{0,30}(?:bluetooth|earphone|headphone|charger|cable|electronic).{0,40}(?:bad|worst|not working|broken|defective|cheap|waste)"]),

    # OPERATIONAL THEMES (track but don't promote)
    ("O1", "Delivery speed complaints", "operational",
     [r"(?:late|delay|slow|took|waiting|wait|not delivered|didn't deliver|hours?|long time).{0,40}(?:deliver|delivery|order|arrive|come|reach)",
      r"(?:deliver|delivery).{0,30}(?:late|delay|slow|not come|didn't come|hours|took)"]),

    ("O2", "App technical issues", "operational",
     [r"(?:crash|bug|error|glitch|hang|freeze|not (?:open|load|work)|login|otp|update|version).{0,40}(?:app|application|screen|phone)",
      r"(?:app|application).{0,40}(?:crash|bug|error|glitch|hang|freeze|not working|not opening|slow)"]),

    ("O3", "Payment/billing issues", "operational",
     [r"(?:payment|pay|transaction|debit|charged|deducted|money|amount|wallet|paytm|upi|gpay).{0,40}(?:fail|error|wrong|issue|problem|stuck|not|double|extra|deducted|cut)",
      r"(?:coupon|promo|discount|offer|code|voucher|cashback).{0,40}(?:not|didn't|doesn't|fail|error|expired|invalid|working)"]),

    ("O4", "Delivery partner behavior", "operational",
     [r"(?:delivery (?:boy|guy|partner|person|man|executive|agent)).{0,40}(?:rude|bad|argue|fight|threaten|steal|misbehav|unprofessional|call|phone|ask)",
      r"(?:rude|argue|fight|threaten|misbehav|unprofessional).{0,30}(?:delivery|driver|rider)"]),
]

# ---- CLASSIFY EACH REVIEW ----
classified = defaultdict(list)  # theme_id -> list of review dicts
unclassified = []

for r in substantive:
    text = r.get('cleaned_text', '').lower()
    matched_themes = []

    for theme_id, label, classification, patterns in RULES:
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                matched_themes.append((theme_id, label, classification))
                break

    if matched_themes:
        for tid, label, cls in matched_themes:
            classified[tid].append({
                'text': r.get('cleaned_text',''),
                'rating': r.get('rating',''),
                'source': r.get('source',''),
                'theme_id': tid,
                'theme_label': label,
                'classification': cls
            })
    else:
        unclassified.append(r)

# ---- REPORT ----
print("=" * 80)
print("THEME EXTRACTION RESULTS")
print("=" * 80)
print()

behavioral_themes = []
operational_themes = []

for theme_id, label, classification, patterns in RULES:
    items = classified.get(theme_id, [])
    count = len(items)
    if count == 0:
        continue

    rating_dist = Counter(i['rating'] for i in items)
    pct = round(100 * count / len(substantive), 1)

    entry = {
        'theme_id': theme_id,
        'label': label,
        'classification': classification,
        'count': count,
        'pct_of_substantive': pct,
        'rating_dist': dict(rating_dist),
        'sample_quotes': [i['text'][:250] for i in items[:8]]
    }

    if classification == 'behavioral':
        behavioral_themes.append(entry)
    else:
        operational_themes.append(entry)

print("--- BEHAVIORAL THEMES (sorted by count) ---")
for t in sorted(behavioral_themes, key=lambda x: x['count'], reverse=True):
    print(f"\n  [{t['theme_id']}] {t['label']}")
    print(f"      Count: {t['count']} ({t['pct_of_substantive']}% of substantive)")
    print(f"      Rating distribution: {t['rating_dist']}")
    print(f"      Sample quotes:")
    for q in t['sample_quotes'][:3]:
        print(f"        - \"{q[:180]}...\"" if len(q)>180 else f"        - \"{q}\"")

print()
print("--- OPERATIONAL THEMES (tracked, not promoted) ---")
for t in sorted(operational_themes, key=lambda x: x['count'], reverse=True):
    print(f"\n  [{t['theme_id']}] {t['label']}")
    print(f"      Count: {t['count']} ({t['pct_of_substantive']}% of substantive)")

print(f"\n--- UNCLASSIFIED: {len(unclassified)} reviews ({round(100*len(unclassified)/len(substantive),1)}%) ---")

# Dump sample unclassified to see what we're missing
print("  Sample unclassified:")
import random
random.seed(99)
for r in random.sample(unclassified, min(15, len(unclassified))):
    print(f"    [{r.get('rating','')}] \"{r.get('cleaned_text','')[:200]}\"")

# Save full results for the artifact
output = {
    'meta': {
        'total_reviews': len(rows),
        'substantive_reviews': len(substantive),
        'short_noise_discarded': len(rows) - len(substantive),
        'source_coverage': {'play_store': len(rows), 'app_store': 0, 'reddit': 0},
        'source_coverage_warning': 'ALL data comes from Play Store only. App Store and Reddit scrapers returned empty. Evidence coverage is single-source.'
    },
    'behavioral_themes': sorted(behavioral_themes, key=lambda x: x['count'], reverse=True),
    'operational_themes': sorted(operational_themes, key=lambda x: x['count'], reverse=True),
    'unclassified_count': len(unclassified)
}

with open('data/results/rigorous_theme_extraction.json', 'w') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("\nSaved to data/results/rigorous_theme_extraction.json")
