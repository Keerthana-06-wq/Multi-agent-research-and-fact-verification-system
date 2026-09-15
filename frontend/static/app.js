document.addEventListener("DOMContentLoaded", () => {
  const API_BASE = (window.BACKEND_URL || "").replace(/\/$/, "");
  const form = document.getElementById("verify-form");
  const queryInput = document.getElementById("query-input");
  const clearBtn = document.getElementById("clear-btn");
  const submitBtn = document.getElementById("submit-btn");
  const btnText = document.getElementById("btn-text");
  const btnSpinner = document.getElementById("btn-spinner");
  const demoContainer = document.getElementById("demo-cases-container");

  const errorCard = document.getElementById("error-card");
  const errorMessage = document.getElementById("error-message");
  const placeholderBox = document.getElementById("placeholder-box");
  const verificationCard = document.getElementById("verification-card");

  // Left Column Verification Elements
  const verdictBanner = document.getElementById("verdict-banner");
  const verdictBadge = document.getElementById("verdict-badge");
  const categoryBadge = document.getElementById("category-badge");
  const confidenceVal = document.getElementById("confidence-val");
  const confidenceBar = document.getElementById("confidence-bar");

  const statedClaim = document.getElementById("stated-claim");
  const correctionBox = document.getElementById("correction-box");
  const correctStatementText = document.getElementById("correct-statement-text");

  const subClaimsBox = document.getElementById("sub-claims-box");
  const subClaimsList = document.getElementById("sub-claims-list");

  const explanationText = document.getElementById("explanation-text");
  const evidenceContainer = document.getElementById("evidence-container");
  const evidenceList = document.getElementById("evidence-list");

  // Right Column Source Inspector & History
  const sourcesContainer = document.getElementById("sources-list");
  const sourcesEmptyState = document.getElementById("sources-empty-state");
  const sourcesCount = document.getElementById("sources-count");

  const historyList = document.getElementById("history-list");
  const historyEmptyState = document.getElementById("history-empty-state");
  const clearHistoryBtn = document.getElementById("clear-history-btn");

  const STORAGE_KEY = "veritas_verification_history_v2";

  // Handle Input Clear Button
  queryInput.addEventListener("input", () => {
    if (queryInput.value.trim().length > 0) {
      clearBtn.classList.remove("hidden");
    } else {
      clearBtn.classList.add("hidden");
    }
  });

  clearBtn.addEventListener("click", () => {
    queryInput.value = "";
    clearBtn.classList.add("hidden");
    queryInput.focus();
  });

  // History Management
  function getHistory() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
    } catch {
      return [];
    }
  }

  function saveHistoryItem(item) {
    let history = getHistory();
    // Prevent duplicate entries of the same query at the top
    history = history.filter(h => h.query.toLowerCase() !== item.query.toLowerCase());
    history.unshift(item);
    if (history.length > 20) history.pop();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    renderHistory();
  }

  function renderHistory() {
    const history = getHistory();
    historyList.innerHTML = "";

    if (history.length === 0) {
      historyEmptyState.classList.remove("hidden");
      return;
    }

    historyEmptyState.classList.add("hidden");

    history.forEach(item => {
      const row = document.createElement("div");
      row.className = "history-item p-2.5 rounded border border-[#ded8cb] bg-[#faf8f3] cursor-pointer text-xs flex items-center justify-between gap-2 shadow-2xs";

      let vBadgeColor = "bg-[#ede8dc] text-[#5c5243] border-[#d8d0bf]";
      if (item.verdict === "TRUE") vBadgeColor = "bg-[#edf5ee] text-[#264f2b] border-[#bed6c1]";
      else if (item.verdict === "FALSE") vBadgeColor = "bg-[#fbf0f0] text-[#7f1c1c] border-[#ecc5c5]";

      row.innerHTML = `
        <div class="truncate flex-grow">
          <div class="font-medium text-[#2b251e] truncate">${escapeHtml(item.query)}</div>
          <div class="text-3xs text-[#8c8273]">${escapeHtml(item.category || 'General')} &bull; ${escapeHtml(item.time)}</div>
        </div>
        <span class="px-2 py-0.5 rounded text-3xs font-black uppercase tracking-wider border ${vBadgeColor} flex-shrink-0">
          ${item.verdict}
        </span>
      `;

      row.addEventListener("click", () => {
        queryInput.value = item.query;
        clearBtn.classList.remove("hidden");
        executeVerification(item.query);
      });

      historyList.appendChild(row);
    });
  }

  clearHistoryBtn.addEventListener("click", () => {
    localStorage.removeItem(STORAGE_KEY);
    renderHistory();
  });

  renderHistory();

  // Load Preset Benchmarks
  async function loadPresetCases() {
    try {
      const res = await fetch(`${API_BASE}/api/preset-cases`);
      if (!res.ok) return;
      const cases = await res.json();
      demoContainer.innerHTML = "";

      cases.forEach((c) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "pill-btn text-3xs px-2.5 py-1 rounded border bg-[#faf8f3] border-[#ded7c8] text-[#4d4437] hover:bg-[#ede7da] font-medium flex items-center gap-1.5 shadow-2xs";

        let dotColor = "bg-[#8c8273]";
        if (c.expected_verdict === "TRUE") dotColor = "bg-[#2d6325]";
        else if (c.expected_verdict === "FALSE") dotColor = "bg-[#9e2424]";

        btn.innerHTML = `
          <span class="w-1.5 h-1.5 rounded-full ${dotColor}"></span>
          <span>${escapeHtml(c.label)}</span>
        `;

        btn.title = `${c.category} - Expected: ${c.expected_verdict}\n${c.description}`;

        btn.addEventListener("click", () => {
          queryInput.value = c.query;
          clearBtn.classList.remove("hidden");
          executeVerification(c.query);
        });

        demoContainer.appendChild(btn);
      });
    } catch (err) {
      console.warn("Could not load preset cases:", err);
    }
  }

  loadPresetCases();

  // Form Submit
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const query = queryInput.value.trim();
    if (!query) return;
    executeVerification(query);
  });

  async function executeVerification(query) {
    submitBtn.disabled = true;
    btnText.textContent = "Verifying...";
    btnSpinner.classList.remove("hidden");
    errorCard.classList.add("hidden");

    try {
      const response = await fetch(`${API_BASE}/api/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query })
      });

      if (!response.ok) {
        throw new Error(`Server status ${response.status}`);
      }

      const data = await response.json();
      renderResult(data);

      // Save to recent verification history
      saveHistoryItem({
        query: query,
        verdict: data.verdict,
        category: data.category,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      });

      placeholderBox.classList.add("hidden");
      verificationCard.classList.remove("hidden");
      verificationCard.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (error) {
      console.error("Verification failed:", error);
      errorMessage.textContent = "Unable to complete verification. Please verify network access or server status.";
      errorCard.classList.remove("hidden");
    } finally {
      submitBtn.disabled = false;
      btnText.textContent = "Verify Claim";
      btnSpinner.classList.add("hidden");
    }
  }

  function renderResult(data) {
    // 1. Verdict & Category Badges
    const verdict = data.verdict || "UNVERIFIED";
    verdictBadge.textContent = verdict;
    verdictBadge.className = "px-3 py-1 rounded text-xs font-black uppercase tracking-wider ";

    verdictBanner.className = "px-5 py-3.5 border-b flex flex-wrap items-center justify-between gap-3 ";

    if (verdict === "TRUE") {
      verdictBadge.classList.add("verdict-true");
      verdictBanner.classList.add("bg-[#eef5ee]", "border-[#bed6c1]");
    } else if (verdict === "FALSE") {
      verdictBadge.classList.add("verdict-false");
      verdictBanner.classList.add("bg-[#faeded]", "border-[#ecc5c5]");
    } else {
      verdictBadge.classList.add("verdict-unverified");
      verdictBanner.classList.add("bg-[#f2efe9]", "border-[#ded7c8]");
    }

    categoryBadge.textContent = data.category || "General Knowledge";

    // Confidence
    const conf = data.confidence ?? 50;
    confidenceVal.textContent = `${conf}%`;
    confidenceBar.style.width = `${conf}%`;

    // 2. Claim
    statedClaim.textContent = data.claim;

    // 3. Highlighted Correction Box (When FALSE)
    if (verdict === "FALSE" && data.correct_statement) {
      correctStatementText.textContent = data.correct_statement;
      correctionBox.classList.remove("hidden");
    } else {
      correctionBox.classList.add("hidden");
    }

    // 4. Multiple Claims Breakdown (Step 12)
    if (data.sub_claims && data.sub_claims.length > 0) {
      subClaimsList.innerHTML = "";
      data.sub_claims.forEach((sc, idx) => {
        const item = document.createElement("div");
        item.className = "p-2.5 rounded bg-[#faf8f3] border border-[#ded8cb] text-2xs";
        const vColor = sc.verdict === "TRUE" ? "text-[#264f2b] bg-[#edf5ee] border-[#bed6c1]" : "text-[#7f1c1c] bg-[#fbf0f0] border-[#ecc5c5]";
        item.innerHTML = `
          <div class="flex items-center justify-between font-bold mb-1">
            <span class="text-[#29241e]">Part ${idx + 1}: ${escapeHtml(sc.claim)}</span>
            <span class="px-2 py-0.5 rounded border text-3xs uppercase font-black ${vColor}">${sc.verdict}</span>
          </div>
          <p class="text-[#696053]">${escapeHtml(sc.explanation)}</p>
        `;
        subClaimsList.appendChild(item);
      });
      subClaimsBox.classList.remove("hidden");
    } else {
      subClaimsBox.classList.add("hidden");
    }

    // 5. Explanation
    explanationText.textContent = data.explanation || "No explanation recorded.";

    // 6. Evidence Points
    evidenceList.innerHTML = "";
    if (data.evidence && data.evidence.length > 0) {
      data.evidence.forEach(item => {
        const li = document.createElement("li");
        li.className = "flex items-start gap-2 bg-[#faf8f3] p-2 rounded border border-[#ded7c8] text-2xs";
        li.innerHTML = `
          <span class="text-[#8c8273] font-mono select-none mt-0.5">▸</span>
          <span class="text-[#3b342b] leading-relaxed">${escapeHtml(item)}</span>
        `;
        evidenceList.appendChild(li);
      });
      evidenceContainer.classList.remove("hidden");
    } else {
      evidenceContainer.classList.add("hidden");
    }

    // 7. Right Column: Source Inspector
    sourcesContainer.innerHTML = "";
    if (data.sources && data.sources.length > 0) {
      sourcesCount.textContent = `${data.sources.length} cited source(s)`;
      sourcesEmptyState.classList.add("hidden");

      data.sources.forEach(src => {
        const card = document.createElement("div");
        card.className = "bg-[#faf8f3] p-3 rounded border border-[#ded8cb] hover:border-[#b8ad9c] transition shadow-2xs space-y-1";

        const tierClass = getTierClass(src.tier);

        card.innerHTML = `
          <div class="flex items-center justify-between gap-1.5">
            <span class="text-3xs font-semibold px-2 py-0.5 rounded ${tierClass}">${escapeHtml(src.tier || 'Source')}</span>
            <span class="text-3xs text-[#73695b] font-mono">${escapeHtml(src.domain)}</span>
          </div>
          <div class="font-medium text-xs text-[#1e1914] pt-0.5">
            <a href="${escapeHtml(src.url)}" target="_blank" rel="noopener noreferrer" class="hover:underline text-[#6e2c16] hover:text-[#451909] inline-flex items-center gap-1 font-semibold">
              ${escapeHtml(src.title)}
              <svg class="w-2.5 h-2.5 text-[#9e9383]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
              </svg>
            </a>
          </div>
          <p class="text-2xs text-[#5e5446] leading-relaxed line-clamp-3">${escapeHtml(src.snippet)}</p>
          <div class="text-3xs text-[#8c8273] pt-0.5">
            Authority Index: <strong class="text-[#3b342b]">${src.credibility_score}%</strong>
          </div>
        `;
        sourcesContainer.appendChild(card);
      });
    } else {
      sourcesCount.textContent = "0 sources";
      sourcesEmptyState.classList.remove("hidden");
    }
  }

  function getTierClass(tier) {
    if (!tier) return "tier-general";
    const lower = tier.toLowerCase();
    if (lower.includes("government")) return "tier-government";
    if (lower.includes("academic")) return "tier-academic";
    if (lower.includes("scientific")) return "tier-scientific";
    if (lower.includes("reference") || lower.includes("encyclopedia")) return "tier-reference";
    if (lower.includes("news")) return "tier-news";
    return "tier-general";
  }

  function escapeHtml(text) {
    if (!text) return "";
    return String(text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});
