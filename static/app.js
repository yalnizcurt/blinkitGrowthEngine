document.addEventListener("DOMContentLoaded", () => {
    const API_BASE = window.API_BASE_URL || "";
    let rawResultsData = [];
    let currentFilter = "all";
    let pollInterval = null;
    let chatHistory = [];

    // DOM Elements
    const totalCountEl = document.getElementById("metric-total-count");
    const promotedCountEl = document.getElementById("metric-promoted-count");
    const monitorCountEl = document.getElementById("metric-monitor-count");
    const nicheCountEl = document.getElementById("metric-niche-count");

    const quadPromoteEl = document.getElementById("quad-promote-list");
    const quadMonitorEl = document.getElementById("quad-monitor-list");
    const quadNicheEl = document.getElementById("quad-niche-list");
    const quadDropEl = document.getElementById("quad-drop-list");

    const promotedContainerEl = document.getElementById("promoted-hypotheses-container");
    const explorerTableBody = document.getElementById("explorer-table-body");

    const searchInput = document.getElementById("theme-search-input");
    const filterPillsContainer = document.getElementById("filter-pills-container");

    const exportCsvBtn = document.getElementById("export-csv-btn");

    // Modal Elements
    const modalOverlay = document.getElementById("theme-modal");
    const modalCloseBtn = document.getElementById("modal-close-btn");
    const modalContentArea = document.getElementById("modal-content-area");

    // Live Fetch Modal Elements
    const fetchModal = document.getElementById("fetch-modal");
    const fetchModalCloseBtn = document.getElementById("fetch-modal-close-btn");
    const openFetchModalBtn = document.getElementById("open-fetch-modal-btn");
    const headerFetchBtn = document.getElementById("header-fetch-btn");
    const liveFetchForm = document.getElementById("live-fetch-form");
    const fetchCancelBtn = document.getElementById("fetch-cancel-btn");
    const fetchStatusBox = document.getElementById("fetch-status-box");
    const fetchStatusText = document.getElementById("fetch-status-text");
    const fetchSubmitBtn = document.getElementById("fetch-submit-btn");

    // AI Chat Elements
    const chatDrawer = document.getElementById("chat-drawer");
    const chatDrawerCloseBtn = document.getElementById("chat-drawer-close-btn");
    const chatFabBtn = document.getElementById("chat-fab-btn");
    const headerChatBtn = document.getElementById("header-chat-btn");
    const navChatBtn = document.getElementById("nav-chat-btn");
    const chatMessagesContainer = document.getElementById("chat-messages-container");
    const chatInput = document.getElementById("chat-input");
    const chatSendBtn = document.getElementById("chat-send-btn");

    // Fetch initial data
    fetchResultsData();

    async function fetchResultsData() {
        try {
            const resp = await fetch(API_BASE + "/api/results");
            if (!resp.ok) throw new Error("Failed to load results data");
            const data = await resp.json();

            rawResultsData = data.themes || [];
            const meta = data.metadata || {};

            // Render Metrics
            totalCountEl.textContent = meta.total_feedback_analyzed || 1951;

            const promotedThemes = rawResultsData.filter(t => t.action === "Promote to Suggested Research Question");
            const monitorThemes = rawResultsData.filter(t => t.action.includes("Monitor"));
            const nicheThemes = rawResultsData.filter(t => t.action.includes("Niche"));
            const outOfScopeThemes = rawResultsData.filter(t => t.action.includes("Out of Scope") || t.action.includes("Drop"));

            promotedCountEl.textContent = promotedThemes.length;
            monitorCountEl.textContent = monitorThemes.length;
            nicheCountEl.textContent = outOfScopeThemes.length;

            // Render Matrix Quadrants
            renderMatrixQuadrants(promotedThemes, monitorThemes, nicheThemes, outOfScopeThemes);

            // Render Promoted Research Cards
            renderPromotedCards(promotedThemes);

            // Render Table
            renderExplorerTable(rawResultsData);

        } catch (err) {
            console.error("Error fetching engine results:", err);
        }
    }

    function renderMatrixQuadrants(promoted, monitor, niche, drop) {
        renderQuadList(quadPromoteEl, promoted);
        renderQuadList(quadMonitorEl, monitor);
        renderQuadList(quadNicheEl, niche);
        renderQuadList(quadDropEl, drop);
    }

    function renderQuadList(container, items) {
        if (!items || items.length === 0) {
            container.innerHTML = `<p class="quad-desc">No themes in this quadrant.</p>`;
            return;
        }

        container.innerHTML = items.map(t => `
            <div class="quad-card" onclick="window.openThemeModal('${escapeQuotes(t.theme)}')">
                <h4>${t.theme}</h4>
                <div class="quad-card-meta">
                    <span>Mentions: ${t.frequency}</span>
                    <span>Prev: ${t.prevalence_score} | Sig: ${t.signal_strength_score}</span>
                </div>
            </div>
        `).join("");
    }

    function renderPromotedCards(promoted) {
        if (!promoted || promoted.length === 0) {
            promotedContainerEl.innerHTML = `<p class="subtitle">No themes met the dual High Prevalence + High Signal threshold yet.</p>`;
            return;
        }

        promotedContainerEl.innerHTML = promoted.map((p, idx) => `
            <div class="screener-card">
                <div class="screener-card-header">
                    <h3 class="screener-card-title">${idx + 1}. ${p.theme}</h3>
                    <span class="score-badge">Prevalence: ${p.prevalence_score}/5.0 | Signal: ${p.signal_strength_score}/5.0</span>
                </div>

                <div style="display: flex; gap: 10px; margin-bottom: 12px; font-size: 12px;">
                    <span class="area-badge">Product Area: ${p.primary_issue || 'General'}</span>
                    <span class="area-badge" style="background: rgba(70, 72, 212, 0.1); color: var(--color-primary);">Journey Stage: ${p.customer_journey_stage || 'Evaluation'}</span>
                    <span class="score-badge" style="background: rgba(46, 125, 50, 0.1); color: #2e7d32;">Impact: ${p.business_impact || 'High'} | Confidence: ${p.confidence || 'High'}</span>
                </div>

                <div class="insight-box" style="margin-bottom: 10px;">
                    <div class="insight-title">Observed Behavior (WHAT)</div>
                    <p style="font-weight: 500;">${p.observed_behavior || "Users avoid non-grocery purchases."}</p>
                </div>

                <div class="insight-box" style="background: rgba(70, 72, 212, 0.05); border-left-color: var(--color-primary); margin-bottom: 10px;">
                    <div class="insight-title" style="color: var(--color-primary);">Visual Causal Chain</div>
                    <p style="font-size: 12px; font-family: monospace; color: var(--color-on-background); font-weight: 500;">${p.causal_chain || p.reasoning_trace || ''}</p>
                </div>

                <div class="insight-box" style="background: rgba(245, 158, 11, 0.08); border-left-color: #f59e0b; margin-bottom: 10px;">
                    <div class="insight-title" style="color: #b45309;">Behavioral Mechanism (WHY)</div>
                    <p style="font-style: italic;">"${p.behavioral_mechanism || "Psychological friction."}"</p>
                </div>

                <div class="insight-box" style="margin-bottom: 10px;">
                    <div class="insight-title">Product Opportunity (Solution-Agnostic)</div>
                    <p style="font-weight: 600; color: var(--color-primary);">🚀 ${p.product_opportunity || p.suggested_insight || "Capability to enable."}</p>
                </div>

                <div class="question-box">
                    <div class="question-title">Suggested 30-Min Non-Leading Research Question</div>
                    <p class="question-text">"${p.suggested_research_question || (p.research_questions && p.research_questions[0]) || ''}"</p>
                    <button class="copy-btn" onclick="window.copyToClipboard('${escapeQuotes(p.suggested_research_question || (p.research_questions && p.research_questions[0]) || '')}')">📋 Copy Question for Screener</button>
                </div>

                <div class="quotes-list">
                    <strong style="font-size: 12px; color: var(--color-on-surface-variant);">Representative Customer Evidence:</strong>
                    ${(p.example_quotes || []).slice(0, 2).map(q => `<div class="quote-item">"${q}"</div>`).join("")}
                </div>
            </div>
        `).join("");
    }

    function renderExplorerTable(items) {
        let filtered = items.filter(item => {
            if (currentFilter === "promote") return item.action === "Promote to Suggested Research Question";
            if (currentFilter === "monitor") return item.action.includes("Monitor");
            if (currentFilter === "niche") return item.action.includes("Niche");
            if (currentFilter === "out_of_scope") return item.action.includes("Out of Scope");
            return true;
        });

        const query = searchInput.value.toLowerCase().trim();
        if (query) {
            filtered = filtered.filter(item => 
                item.theme.toLowerCase().includes(query) ||
                (item.primary_issue || "").toLowerCase().includes(query) ||
                item.action.toLowerCase().includes(query) ||
                (item.example_quotes || []).some(q => q.toLowerCase().includes(query))
            );
        }

        if (filtered.length === 0) {
            explorerTableBody.innerHTML = `<tr><td colspan="10" style="text-align: center; color: var(--color-on-surface-variant); padding: 24px;">No matching themes found.</td></tr>`;
            return;
        }

        explorerTableBody.innerHTML = filtered.map(t => `
            <tr>
                <td><strong>${t.theme}</strong></td>
                <td><span class="area-badge">${t.primary_issue || 'General'}</span></td>
                <td><span class="area-badge" style="background: rgba(0,0,0,0.05);">${t.customer_journey_stage || 'Evaluation'}</span></td>
                <td><span class="relevance-badge ${getRelevanceBadgeClass(t.research_relevance)}">${t.research_relevance || 'NO'}</span></td>
                <td><span class="quad-badge ${getBadgeClass(t.action)}">${t.action}</span></td>
                <td>${t.prevalence_score} / 5.0</td>
                <td>${t.signal_strength_score} / 5.0</td>
                <td>${t.frequency}</td>
                <td>${(t.sources || []).join(", ")}</td>
                <td><button class="pill-btn" onclick="window.openThemeModal('${escapeQuotes(t.theme)}')">View</button></td>
            </tr>
        `).join("");
    }

    function getBadgeClass(action) {
        if (action.includes("Promote")) return "badge-green";
        if (action.includes("Monitor")) return "badge-yellow";
        if (action.includes("Niche")) return "badge-blue";
        if (action.includes("Out of Scope")) return "badge-red";
        return "badge-gray";
    }

    function getRelevanceBadgeClass(relevance) {
        if (relevance === "DIRECT" || relevance === "YES") return "badge-green";
        if (relevance === "INDIRECT" || relevance === "PARTIAL") return "badge-yellow";
        return "badge-gray";
    }

    // Modal Details Window with Full 10-Step Reasoning Chain
    window.openThemeModal = (themeTitle) => {
        const themeObj = rawResultsData.find(t => t.theme === themeTitle);
        if (!themeObj) return;

        modalContentArea.innerHTML = `
            <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 12px; flex-wrap: wrap;">
                <span class="quad-badge ${getBadgeClass(themeObj.action)}">${themeObj.action}</span>
                <span class="area-badge" style="background: rgba(0,0,0,0.05); padding: 4px 8px; border-radius: 4px; font-size: 12px;">Area: ${themeObj.primary_issue || 'General'}</span>
                <span class="area-badge" style="background: rgba(70, 72, 212, 0.1); color: var(--color-primary); padding: 4px 8px; border-radius: 4px; font-size: 12px;">Stage: ${themeObj.customer_journey_stage || 'Evaluation'}</span>
                <span class="relevance-badge ${getRelevanceBadgeClass(themeObj.research_relevance)}" style="padding: 4px 8px; border-radius: 4px; font-size: 12px;">Relevance: ${themeObj.research_relevance || 'NO'}</span>
            </div>

            <h2 style="font-family: 'Outfit', sans-serif; font-size: 22px; margin-bottom: 12px;">${themeObj.theme}</h2>

            <div style="background: var(--color-surface-low); padding: 14px; border-radius: 8px; margin-bottom: 16px; border: 1px solid var(--color-outline-variant);">
                <strong style="font-size: 13px;">Full Auditable Reasoning Chain:</strong>
                <p style="font-size: 12px; font-family: monospace; color: var(--color-primary); margin-top: 6px; white-space: pre-wrap;">${themeObj.reasoning_trace || "Evidence -> Behavior -> Mechanism -> Opportunity"}</p>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px;">
                <div style="background: #ffffff; padding: 12px; border-radius: 8px; border: 1px solid var(--color-outline-variant);">
                    <strong style="font-size: 12px; color: var(--color-on-surface-variant);">Observed Facts:</strong>
                    <ul style="font-size: 12px; margin-top: 4px; padding-left: 16px;">
                        ${(themeObj.observed_facts || []).map(f => `<li>${f}</li>`).join("")}
                    </ul>
                </div>
                <div style="background: #ffffff; padding: 12px; border-radius: 8px; border: 1px solid var(--color-outline-variant);">
                    <strong style="font-size: 12px; color: var(--color-on-surface-variant);">Behavioral Mechanism (WHY):</strong>
                    <p style="font-size: 12px; margin-top: 4px; font-style: italic;">"${themeObj.behavioral_mechanism || 'N/A'}"</p>
                </div>
            </div>

            ${themeObj.product_opportunity ? `
            <div class="insight-box" style="margin-bottom: 16px;">
                <div class="insight-title">Product Opportunity (Solution-Agnostic)</div>
                <p style="font-weight: 600;">🚀 ${themeObj.product_opportunity}</p>
            </div>
            ` : ""}

            ${themeObj.research_hypothesis ? `
            <div class="insight-box" style="background: rgba(46, 125, 50, 0.08); border-left-color: #2e7d32; margin-bottom: 16px;">
                <div class="insight-title" style="color: #2e7d32;">Testable Research Hypothesis</div>
                <p>🧪 "${themeObj.research_hypothesis}"</p>
            </div>
            ` : ""}

            ${themeObj.suggested_research_question ? `
            <div class="question-box" style="margin-bottom: 16px;">
                <div class="question-title">Suggested 30-Min Non-Leading Research Question</div>
                <p class="question-text">"${themeObj.suggested_research_question}"</p>
                <button class="copy-btn" onclick="window.copyToClipboard('${escapeQuotes(themeObj.suggested_research_question)}')">📋 Copy Question for Screener</button>
            </div>
            ` : ""}

            ${themeObj.action.includes("Out of Scope") ? `
            <div class="insight-box" style="border-left-color: #ef4444; background: rgba(239, 68, 68, 0.08);">
                <div class="insight-title" style="color: #c5221f;">Status: Out of Scope for Research Objective</div>
                <p>${themeObj.out_of_scope_reason || "This theme is important for product improvement but does not explain category exploration."}</p>
            </div>
            ` : ""}

            <div class="quotes-list" style="margin-top: 16px;">
                <strong style="font-size: 13px; color: var(--color-on-surface-variant);">Representative Verbatim Customer Evidence:</strong>
                ${(themeObj.example_quotes || []).map(q => `<div class="quote-item" style="margin-top: 6px; font-style: italic;">"${q}"</div>`).join("")}
            </div>
        `;

        modalOverlay.classList.add("active");
    };

    modalCloseBtn.addEventListener("click", () => modalOverlay.classList.remove("active"));
    modalOverlay.addEventListener("click", (e) => {
        if (e.target === modalOverlay) modalOverlay.classList.remove("active");
    });

    // Copy Helper
    window.copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
        alert("Copied research question to clipboard!");
    };

    function escapeQuotes(str) {
        return (str || "").replace(/'/g, "\\'").replace(/"/g, "&quot;");
    }

    // Filter pills
    filterPillsContainer.addEventListener("click", (e) => {
        if (e.target.classList.contains("pill-btn")) {
            document.querySelectorAll(".filter-pills .pill-btn").forEach(b => b.classList.remove("active"));
            e.target.classList.add("active");
            currentFilter = e.target.dataset.filter;
            renderExplorerTable(rawResultsData);
        }
    });

    searchInput.addEventListener("input", () => renderExplorerTable(rawResultsData));

    // Export CSV
    exportCsvBtn.addEventListener("click", () => {
        window.open(API_BASE + "/api/download-csv", "_blank");
    });

    // AI Chat Drawer Controls
    const openChatDrawer = () => chatDrawer.classList.add("active");
    const closeChatDrawer = () => chatDrawer.classList.remove("active");

    if (chatFabBtn) chatFabBtn.addEventListener("click", openChatDrawer);
    if (headerChatBtn) headerChatBtn.addEventListener("click", openChatDrawer);
    if (navChatBtn) navChatBtn.addEventListener("click", (e) => {
        e.preventDefault();
        openChatDrawer();
    });
    if (chatDrawerCloseBtn) chatDrawerCloseBtn.addEventListener("click", closeChatDrawer);

    // Quick Prompt Pills Click Handlers
    document.querySelectorAll(".chat-pill-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const promptText = btn.dataset.prompt;
            chatInput.value = promptText;
            sendChatMessage();
        });
    });

    chatSendBtn.addEventListener("click", sendChatMessage);
    chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") sendChatMessage();
    });

    async function sendChatMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        // Append User Message
        appendChatMessage("user", text);
        chatInput.value = "";
        chatHistory.push({ role: "user", content: text });

        // Show AI Typing Indicator
        const loadingMsgEl = appendChatMessage("ai", "⏳ Analyzing review corpus and generating grounded response...");

        try {
            const resp = await fetch(API_BASE + "/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ messages: chatHistory })
            });

            const data = await resp.json();
            loadingMsgEl.remove();

            if (data.reply) {
                let aiText = data.reply;
                if (data.citations && data.citations.length > 0) {
                    aiText += "\n\n**Cited Verbatim Evidence:**\n" + data.citations.map(c => `> *"${c.quote}"* — [Theme: ${c.theme}]`).join("\n");
                }
                const msgEl = appendChatMessage("ai", aiText);

                // Render Follow-up Pills
                if (data.suggested_followups && data.suggested_followups.length > 0) {
                    const followUpDiv = document.createElement("div");
                    followUpDiv.style.cssText = "display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px;";
                    data.suggested_followups.forEach(fText => {
                        const pill = document.createElement("button");
                        pill.className = "chat-pill-btn";
                        pill.style.cssText = "font-size: 11px; background: rgba(70, 72, 212, 0.08); border-color: rgba(70, 72, 212, 0.2);";
                        pill.textContent = "💬 " + fText;
                        pill.addEventListener("click", () => {
                            chatInput.value = fText;
                            sendChatMessage();
                        });
                        followUpDiv.appendChild(pill);
                    });
                    msgEl.querySelector(".msg-bubble").appendChild(followUpDiv);
                }

                chatHistory.push({ role: "assistant", content: data.reply });
            } else {
                appendChatMessage("ai", "❌ Could not retrieve grounded answer from AI.");
            }
        } catch (err) {
            loadingMsgEl.remove();
            appendChatMessage("ai", "❌ Network error communicating with Groq AI API.");
        }
    }

    function appendChatMessage(role, content) {
        const msgDiv = document.createElement("div");
        msgDiv.className = `chat-msg ${role === "user" ? "user-msg" : "ai-msg"}`;
        
        // Convert simple markdown bold/italics
        const formattedContent = content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');

        msgDiv.innerHTML = `<div class="msg-bubble">${formattedContent}</div>`;
        chatMessagesContainer.appendChild(msgDiv);
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
        return msgDiv;
    }

    // Live Fetch Modal Controls
    const openFetchModal = () => fetchModal.classList.add("active");
    const closeFetchModal = () => {
        fetchModal.classList.remove("active");
        if (pollInterval) clearInterval(pollInterval);
    };

    if (openFetchModalBtn) openFetchModalBtn.addEventListener("click", openFetchModal);
    if (headerFetchBtn) headerFetchBtn.addEventListener("click", openFetchModal);
    if (fetchModalCloseBtn) fetchModalCloseBtn.addEventListener("click", closeFetchModal);
    if (fetchCancelBtn) fetchCancelBtn.addEventListener("click", closeFetchModal);

    // Live Fetch Form Submission
    liveFetchForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const selectedSources = Array.from(document.querySelectorAll("input[name='sources']:checked")).map(cb => cb.value);
        if (selectedSources.length === 0) {
            alert("Please select at least one source.");
            return;
        }

        const psCount = parseInt(document.getElementById("input-ps-count").value, 10) || 500;
        const asCount = parseInt(document.getElementById("input-as-count").value, 10) || 500;
        const redditTermsRaw = document.getElementById("input-reddit-terms").value || "blinkit";
        const redditTerms = redditTermsRaw.split(",").map(s => s.trim()).filter(Boolean);

        fetchSubmitBtn.disabled = true;
        fetchStatusBox.style.display = "block";
        fetchStatusText.textContent = "Starting live fetch & 10-step discovery...";

        try {
            const resp = await fetch(API_BASE + "/api/run-pipeline", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    playstore_count: psCount,
                    appstore_count: asCount,
                    reddit_terms: redditTerms,
                    sources: selectedSources
                })
            });

            const data = await resp.json();
            if (resp.ok) {
                fetchStatusText.textContent = data.message || "Pipeline started. Fetching live reviews...";
                
                if (pollInterval) clearInterval(pollInterval);
                pollInterval = setInterval(async () => {
                    try {
                        const statusResp = await fetch(API_BASE + "/api/status");
                        const statusData = await statusResp.json();
                        if (statusData.status === "running") {
                            fetchStatusText.textContent = statusData.message || "Executing live classification...";
                        } else if (statusData.status === "completed") {
                            clearInterval(pollInterval);
                            fetchStatusText.textContent = "✅ Done! Refreshing dashboard...";
                            setTimeout(() => {
                                closeFetchModal();
                                fetchResultsData();
                                fetchSubmitBtn.disabled = false;
                                fetchStatusBox.style.display = "none";
                            }, 1200);
                        } else if (statusData.status === "error") {
                            clearInterval(pollInterval);
                            fetchStatusText.textContent = "❌ Error: " + statusData.message;
                            fetchSubmitBtn.disabled = false;
                        }
                    } catch (err) {
                        console.error("Status check failed:", err);
                    }
                }, 3000);

            } else {
                fetchStatusText.textContent = "❌ " + (data.message || "Failed to trigger pipeline.");
                fetchSubmitBtn.disabled = false;
            }
        } catch (err) {
            fetchStatusText.textContent = "❌ Network error starting pipeline.";
            fetchSubmitBtn.disabled = false;
        }
    });

    // Sidebar Navigation Active Tab & Scroll Handler
    const navItems = document.querySelectorAll(".nav-menu .nav-item");
    let isManualClicking = false;

    function setActiveNavItem(targetId) {
        navItems.forEach(item => {
            const href = item.getAttribute("href");
            if (href === `#${targetId}`) {
                item.classList.add("active");
            } else {
                item.classList.remove("active");
            }
        });
    }

    navItems.forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            const targetId = item.getAttribute("href").replace("#", "");
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                isManualClicking = true;
                setActiveNavItem(targetId);
                targetSection.scrollIntoView({ behavior: "smooth" });
                if (history.pushState) {
                    history.pushState(null, "", "#" + targetId);
                }
                setTimeout(() => { isManualClicking = false; }, 800);
            }
        });
    });

    // Precise Viewport Focal Distance Scroll Spy
    function updateActiveTabOnScroll() {
        if (isManualClicking) return;

        const sectionIds = ["overview", "matrix", "promoted", "explorer"];
        const scrollBottom = window.scrollY + window.innerHeight;
        const totalHeight = document.documentElement.scrollHeight;

        if (scrollBottom >= totalHeight - 60) {
            setActiveNavItem("explorer");
            return;
        }

        let activeSectionId = "overview";
        let minDistance = Infinity;

        for (const id of sectionIds) {
            const el = document.getElementById(id);
            if (el) {
                const rect = el.getBoundingClientRect();
                if (rect.bottom > 100 && rect.top < window.innerHeight - 100) {
                    const dist = Math.abs(rect.top - 120);
                    if (dist < minDistance) {
                        minDistance = dist;
                        activeSectionId = id;
                    }
                }
            }
        }

        setActiveNavItem(activeSectionId);
    }

    window.addEventListener("scroll", updateActiveTabOnScroll, { passive: true });
    updateActiveTabOnScroll();
});
