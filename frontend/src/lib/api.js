const API_BASE = "";

function getAuthToken() {
  return localStorage.getItem("archivum_token") || "";
}

function setAuthToken(token) {
  if (token) {
    localStorage.setItem("archivum_token", token);
  } else {
    localStorage.removeItem("archivum_token");
  }
  window.dispatchEvent(new CustomEvent("auth-change", { detail: { isAuthenticated: !!token } }));
}

async function request(path, options = {}) {
  const token = getAuthToken();

  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
    ...options,
  });

  const responseText = await response.text();
  let payload = null;

  if (responseText) {
    try {
      payload = JSON.parse(responseText);
    } catch {
      payload = responseText;
    }
  }

  if (!response.ok) {
    const message =
      typeof payload === "string"
        ? payload
        : payload?.detail || `Request failed: ${response.status}`;

    if (response.status === 401) {
      setAuthToken(null);
    }

    throw new Error(message);
  }

  return payload;
}

// ─────────────────────────────────────────────────────────────
// AUTH
// ─────────────────────────────────────────────────────────────

export async function signupUser({ username, email, password }) {
  return request("/auth/signup", {
    method: "POST",
    body: JSON.stringify({ username, email, password }),
  });
}

export async function verifyEmail({ email, verification_code }) {
  return request("/auth/verify-email", {
    method: "POST",
    body: JSON.stringify({ email, verification_code }),
  });
}

export async function resendOtp(email) {
  return request("/auth/resend-otp", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

export async function loginUser({ email, password }) {
  const data = await request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });

  if (data?.access_token) {
    setAuthToken(data.access_token);
  }

  return data;
}

export function logoutUser() {
  setAuthToken(null);
  return true;
}

export async function getCurrentUser() {
  return request("/auth/me");
}

// ─────────────────────────────────────────────────────────────
// LOCAL PAPER SEARCH (database)
// ─────────────────────────────────────────────────────────────

export async function searchPapers(query = "transformer") {
  const params = new URLSearchParams({ q: query });
  const data = await request(`/api/papers/search?${params.toString()}`);
  return data.papers || [];
}

export async function getPaperDetails(paperId) {
  return request(`/api/papers/${paperId}`);
}

// ─────────────────────────────────────────────────────────────
// EXTERNAL PAPER SEARCH (Semantic Scholar + arXiv)
// ─────────────────────────────────────────────────────────────

export async function searchPapersExternal(query, limit = 10) {
  const params = new URLSearchParams({ q: query, limit: String(limit) });
  return request(`/api/search/papers?${params.toString()}`);
}

export async function importPaper(paperData) {
  return request("/api/search/import", {
    method: "POST",
    body: JSON.stringify(paperData),
  });
}

// ─────────────────────────────────────────────────────────────
// LIBRARY
// ─────────────────────────────────────────────────────────────

export async function addToLibrary(paperId) {
  return request("/api/library", {
    method: "POST",
    body: JSON.stringify({ paper_id: paperId }),
  });
}

export async function getLibrary() {
  const data = await request("/api/library");
  return data.papers || [];
}

export async function removeFromLibrary(paperId) {
  return request(`/api/library/${paperId}`, { method: "DELETE" });
}

// ─────────────────────────────────────────────────────────────
// READER PROGRESS
// ─────────────────────────────────────────────────────────────

export async function removeFromReader(paperId) {
  return request(`/api/reader/${paperId}`, { method: "DELETE" });
}

export async function getReaderProgress() {
  return request("/api/reader");
}

export async function getReaderHistory() {
  const data = await request("/api/reader/history");
  return data.papers || [];
}

export async function saveReaderProgress(paperId, currentPage) {
  return request("/api/reader/progress", {
    method: "POST",
    body: JSON.stringify({ paper_id: paperId, current_page: currentPage }),
  });
}

// ─────────────────────────────────────────────────────────────
// PAPER NOTES
// ─────────────────────────────────────────────────────────────

export async function getPaperNotes(paperId) {
  const data = await request(`/api/papers/${paperId}/notes`);
  return data.notes || [];
}

export async function createPaperNote(paperId, title, content) {
  return request(`/api/papers/${paperId}/notes`, {
    method: "POST",
    body: JSON.stringify({ title, content }),
  });
}

export async function updatePaperNote(paperId, noteId, title, content) {
  return request(`/api/papers/${paperId}/notes`, {
    method: "PUT",
    body: JSON.stringify({ id: noteId, title, content }),
  });
}

// ─────────────────────────────────────────────────────────────
// UPLOAD
// ─────────────────────────────────────────────────────────────

export async function uploadPaper(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("/api/papers/upload", {
    method: "POST",
    body: formData,
    headers: {
      ...(getAuthToken() ? { Authorization: `Bearer ${getAuthToken()}` } : {}),
    },
  });

  const responseText = await response.text();
  let payload = null;
  if (responseText) {
    try {
      payload = JSON.parse(responseText);
    } catch {
      payload = responseText;
    }
  }

  if (!response.ok) {
    const message =
      typeof payload === "string" ? payload : payload?.detail || "Upload failed";
    throw new Error(message);
  }

  return payload;
}

// ─────────────────────────────────────────────────────────────
// RAG — ANALYZE PAPER
// ─────────────────────────────────────────────────────────────

export async function analyzePaper(paperId) {
  return request(`/api/papers/${paperId}/analyze`, { method: "POST" });
}

// ─────────────────────────────────────────────────────────────
// RAG — ASK
// ─────────────────────────────────────────────────────────────

export async function askPaper(paperId, question) {
  return request(`/api/papers/${paperId}/ask`, {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}

// ─────────────────────────────────────────────────────────────
// RAG — SUMMARIZE
// ─────────────────────────────────────────────────────────────

export async function summarizePaper(paperId) {
  return request(`/api/papers/${paperId}/summarize`, { method: "POST" });
}

// ─────────────────────────────────────────────────────────────
// RAG — INFORMATION EXTRACTION
// ─────────────────────────────────────────────────────────────

export async function extractPaperInfo(paperId) {
  return request(`/api/papers/${paperId}/extract`, { method: "POST" });
}

// ─────────────────────────────────────────────────────────────
// RAG — RESEARCH GAPS
// ─────────────────────────────────────────────────────────────

export async function getResearchGaps(paperId) {
  return request(`/api/papers/${paperId}/research-gaps`, { method: "POST" });
}

// ─────────────────────────────────────────────────────────────
// RAG — CITATION VERIFICATION
// ─────────────────────────────────────────────────────────────

export async function verifyCitations(paperId, answer) {
  return request(`/api/papers/${paperId}/verify-citations`, {
    method: "POST",
    body: JSON.stringify({ answer }),
  });
}

// ─────────────────────────────────────────────────────────────
// RAG — PAPER COMPARISON
// ─────────────────────────────────────────────────────────────

export async function comparePapers(paperIdA, paperIdB) {
  return request("/api/papers/compare", {
    method: "POST",
    body: JSON.stringify({ paper_id_a: paperIdA, paper_id_b: paperIdB }),
  });
}

// ─────────────────────────────────────────────────────────────
// RAG STATUS
// ─────────────────────────────────────────────────────────────

export async function getRagStatus() {
  return request("/api/rag/status");
}

export { getAuthToken, setAuthToken };
