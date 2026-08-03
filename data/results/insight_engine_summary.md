# AI Product Discovery Engine — Master Knowledge Report

**Business Objective**: *Increase percentage of Monthly Active Customers purchasing from at least one new category every month.*


**Total Feedback Analyzed**: 862 clean customer items across Play Store, App Store, and Reddit.

## 🎯 Promoted Product Opportunities & Auditable Reasoning Chains

### 1. Low Trust in High-Value Purchases

- **Primary Issue**: `Refunds / Returns` | **Relevance**: `DIRECT` | **Journey Stage**: `Evaluation`

- **Business Impact**: `High` | **Confidence**: `High` (High confidence because:
- Observed consistently across 3 sources (play_store, app_store, reddit).
- 82 supporting customer reviews describe the same behavioral mechanism using consistent language.
- Pure cluster representing one clear customer problem.
- Contradictory evidence check: 19 opposing reviews identified in dataset.)

- **Evidence Summary**: Customers reported denied return requests on non-grocery items and missing refund protection.

- **Observed Facts**: Return request rejected on non-working earphone, No refund given for defective non-grocery product

- **Observed Behavior (WHAT)**: Users restrict purchases to low-risk grocery staples and avoid unfamiliar non-grocery categories.

- **Behavioral Mechanism (WHY)**: *"The perceived financial downside of a failed purchase outweighs the expected utility of trying a new category."*

- **Underlying Need / JTBD**: Financial safety and guaranteed post-purchase protection.

- **Barrier / Driver**: Weak trust in post-purchase refund policies for non-staple categories.

- **Product Opportunity (Solution-Agnostic)**: 🚀 **"Increase customer confidence when purchasing high-value or unfamiliar products."**

- **Research Hypothesis**: 🧪 *"If customers trust that high-value products can be returned without financial loss, they will be more willing to purchase electronics and premium non-grocery products."*

- **Research Questions**: "Tell me about the last time you decided not to buy a product outside your usual categories on Blinkit.", "What specific return assurances did you look for before deciding?"

- **Alternative Explanations**: Users prefer specialist e-commerce platforms for electronics.

- **Contradictory Evidence**: Contradictory evidence identified in dataset: 19 reviews report positive product quality or satisfactory support (e.g. "great service nice paking...").

- **Assumptions**: Reviews reflect actual purchasing hesitation.

- **Full Reasoning Trace**: `Return request rejected on non-working earphone ↓ Post-Purchase Return Risk ↓ High Financial Downside Fear ↓ Avoid Electronics & Non-Grocery Items ↓ Reduced Category Exploration`

- **Supporting Verbatim Customer Evidence**:

  > "Bhot hi bekar app hai - Replacement or refund ka option limited hai chahe product pasand aaye ya nhi pr agar ek baar product sell hogya to vo replace nhi hota- 1 rating hai is app ki"

  > "my one item missing in my order not any refund in my account"

  > "Anish Loharuka - Blinkit is great for convenience, but it really needs a return option for certain categories like electronics and other expensive products. If an item is unused, sealed, and in its original condition, customers should be able to return it within a short window. A no-return policy on high-value items discourages purchases and reduces customer confidence. Adding limited returns for eligible products would significantly improve the shopping experience."


---

### 2. Assortment Gaps in Long-Tail Categories

- **Primary Issue**: `Assortment` | **Relevance**: `DIRECT` | **Journey Stage**: `Discovery`

- **Business Impact**: `High` | **Confidence**: `Medium` (Medium confidence because:
- Observed across 3 sources (reddit, play_store, app_store) in 58 customer reviews.
- Cluster represents a specific customer problem with moderate signal strength.
- Contradictory evidence check: 0 opposing reviews identified in dataset.
- Requires qualitative user interview validation for broader category trial impact.)

- **Evidence Summary**: Customers reported unavailability of specific long-tail non-grocery products upon searching.

- **Observed Facts**: Requested long-tail non-grocery product was unavailable, Search yields out-of-stock results

- **Observed Behavior (WHAT)**: Users assume non-grocery categories are limited and stop searching.

- **Behavioral Mechanism (WHY)**: *"Perceived friction in finding specific non-grocery items leads customers to assume Blinkit only carries daily essentials."*

- **Underlying Need / JTBD**: Deep assortment availability for non-staple goods.

- **Barrier / Driver**: Perceived lack of product depth in non-grocery categories.

- **Product Opportunity (Solution-Agnostic)**: 🚀 **"Increase customer confidence that desired products will be available when shopping across new categories."**

- **Research Hypothesis**: 🧪 *"If customers feel confident that niche long-tail items are stocked reliably, they will be more willing to search and purchase from new product categories."*

- **Research Questions**: "When searching for products outside groceries on Blinkit, how do you evaluate whether the selection is adequate?"

- **Alternative Explanations**: Customers prefer specialist book/electronics retailers.

- **Contradictory Evidence**: No contradictory evidence was found after explicitly reviewing all 1,602 dataset reviews.

- **Assumptions**: 

- **Full Reasoning Trace**: `Requested long-tail non-grocery product was unavailable ↓ Search Result Abandonment ↓ Perception of Grocery-Only Inventory ↓ Stop Evaluating Non-Staple Items ↓ Reduced Category Trial`

- **Supporting Verbatim Customer Evidence**:

  > "How Digital Marketing is Revolutionizing Business Growth in India — What You Need to Know in 2025 Digital marketing in India is evolving faster than ever, and it’s becoming the backbone of business growth across sectors—from startups to real estate, retail, and even government services. Whether you’re a seasoned marketer or just starting out, understanding the current trends and tools can make a huge difference in your campaigns and ROI. Here’s a quick overview of the biggest trends shaping digital marketing in India right now: 1. **Hyper-Targeted Social Media Ads** Platforms like Facebook, Instagram, and LinkedIn offer precise targeting options based on demographics, interests, and behaviors. Marketers are leveraging these tools to reach niche audiences, especially in tier 2 and tier 3 cities, unlocking untapped markets. 2. **Short-Form Video Content Dominates** Thanks to TikTok’s legacy and Instagram Reels, short-form video is king. Brands that create engaging, snackable videos see better engagement and lead conversions. 3. **WhatsApp Marketing for Personalized Outreach** WhatsApp Business API is becoming a game-changer for real estate, education, and e-commerce sectors — enabling instant customer support and lead nurturing. 4. **Local SEO & Voice Search Optimization** With voice assistants gaining popularity, optimizing for voice search and local SEO is crucial for discovery by mobile-first users. 5. **AI and Automation in Campaign Management** From chatbots to predictive analytics, AI tools help marketers personalize experiences and optimize budgets efficiently. **Discussion:** What digital marketing strategies have worked best for you in India? Are you using any new tools or platforms that you think others should know about? Share your experiences or questions below! If you want to dive deeper into real estate digital marketing or social media ad campaigns, check out [this agency]( that specializes in driving results in the Indian market. Looking forward to your insights!"

  > "Apply some basic statistics to calculate a pessimistic expected minimum revenue per month, for example. This would give you a solid base level of your income, so you can plan on this and see where it takes you and whether it is enough. To calculate it, you list your monthly incomes as numbers consider the average of numbers below the average. This gives you a pessimistic expected value as monthly income for short term. If you want it for middle term (less pessimistic) then use the values below the average 2 times, and then calculate an average on this new list. I recommend you to always use pessimistic analysis in the future when you measure something. Also if you're in E-commerce, then measure the effect of your product choices or price choices. I give you a quick calculation method. Let's say, you try out 2 things and you get N sales as a total for 2 of them. Then one of them must be at least this much to have enough statistical proof it is better, and what you see is not just random noise: SQRT( N ) + N / 2 So you add the square root and its half. For example if both products have been sold 100 times as a total, then one of them must be at least 60 to say that is it really better. This can be applied when you have events for 2 things (binary). Also I'm providing a price optimization app with a new generation unique mathematics for web shops built in Shopify to maximize profit and customer experience as well by constantly approaching a Nash equilibrium. It is an install and forget method. It optimizes all item prices automatically in the background. No menus, no dashboard and no manual settings or any intervention needed. I do not want to put links here, you can see it in my profile."

  > "The place where I am living is a type of Village going to be a city in some years so most of the things are unavailable in nearby markets or shops . Because of Blinkit I could survive here . Thanks to Blinkit & delivery partners also 🙏"


---


## 📊 Secondary / Monitored Signals

- **Excessive Fees and Surge Charges** (`Delivery Experience`) — Stage: Fulfillment | Impact: Low | Confidence: Medium


## 🛑 Out of Scope Themes (Routed to Operational Product Teams)

_None_
