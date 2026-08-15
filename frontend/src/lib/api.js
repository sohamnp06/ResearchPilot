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
    const message = typeof payload === "string" ? payload : payload?.detail || `Request failed: ${response.status}`;

    if (response.status === 401) {
      setAuthToken(null);
    }

    throw new Error(message);
  }

  return payload;
}

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

export async function searchPapers(query = "transformer") {
  const params = new URLSearchParams({ q: query });
  const data = await request(`/api/papers/search?${params.toString()}`);
  return data.papers || [];
}

export async function getPaperDetails(paperId) {
  const data = await request(`/api/papers/${paperId}`);
  return data;
}

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
  return request(`/api/library/${paperId}`, {
    method: "DELETE",
  });
}

export async function removeFromReader(paperId) {
  return request(`/api/reader/${paperId}`, {
    method: "DELETE",
  });
}

export async function getReaderProgress() {
  return request("/api/reader");
}

export async function saveReaderProgress(paperId, currentPage) {
  return request("/api/reader/progress", {
    method: "POST",
    body: JSON.stringify({ paper_id: paperId, current_page: currentPage }),
  });
}

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

export async function uploadPaper(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`/api/papers/upload`, {
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
    const message = typeof payload === "string" ? payload : payload?.detail || "Upload failed";
    throw new Error(message);
  }

  return payload;
}

export { getAuthToken, setAuthToken };
