import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { resendOtp, verifyEmail } from "../lib/api";

function VerifyEmail() {
  const navigate = useNavigate();
  const location = useLocation();
  const emailFromState = location.state?.email || "";
  const [email, setEmail] = useState(emailFromState);
  const [code, setCode] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleVerify = async (event) => {
    event.preventDefault();
    setError("");
    setMessage("");
    setLoading(true);

    try {
      const result = await verifyEmail({ email, verification_code: code });
      setMessage(result.message || "Email verified successfully");
      setTimeout(() => navigate("/login"), 1200);
    } catch (err) {
      setError(err.message || "Verification failed");
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    setError("");
    setMessage("");
    try {
      const result = await resendOtp(email);
      setMessage(result.message || "Verification code sent");
    } catch (err) {
      setError(err.message || "Unable to resend code");
    }
  };

  return (
    <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", background: "#FFF6EA", color: "#000" }}>
      <div style={{ width: "100%", maxWidth: "520px", background: "#FFF6EA", border: "2px solid #000", padding: "2rem 2rem 1.4rem", boxShadow: "8px 8px 0 #000" }}>
        <h1 style={{ margin: "0 0 1.5rem", textAlign: "center", fontFamily: '"Instrument Serif", serif', fontSize: "64px", fontWeight: 400, lineHeight: 1, letterSpacing: "-0.04em" }}>
          VERIFY EMAIL
        </h1>

        <form onSubmit={handleVerify} style={{ display: "grid", gap: "1rem" }}>
          <div style={{ display: "grid", gap: "0.5rem" }}>
            <label style={{ fontFamily: '"Lexend Exa", sans-serif', fontSize: "12px", letterSpacing: ".12em", textTransform: "uppercase" }}>EMAIL</label>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
              required
              style={{ padding: "0.9rem 1rem", border: "2px solid #000", background: "#FFF6EA", color: "#000", fontFamily: '"JetBrains Mono", monospace', fontSize: "16px", outline: "none" }}
            />
          </div>

          <div style={{ display: "grid", gap: "0.5rem" }}>
            <label style={{ fontFamily: '"Lexend Exa", sans-serif', fontSize: "12px", letterSpacing: ".12em", textTransform: "uppercase" }}>VERIFICATION CODE</label>
            <input
              type="text"
              value={code}
              onChange={(event) => setCode(event.target.value)}
              placeholder="6-digit verification code"
              required
              style={{ padding: "0.9rem 1rem", border: "2px solid #000", background: "#FFF6EA", color: "#000", fontFamily: '"JetBrains Mono", monospace', fontSize: "16px", outline: "none" }}
            />
          </div>

          {message && <div style={{ color: "#166534", fontSize: "0.9rem", fontFamily: '"Lexend Exa", sans-serif' }}>{message}</div>}
          {error && <div style={{ color: "#B91C1C", fontSize: "0.9rem", fontFamily: '"Lexend Exa", sans-serif' }}>{error}</div>}

          <button
            type="submit"
            disabled={loading}
            style={{ padding: "0.9rem 1rem", border: "2px solid #000", background: "#111827", color: "#fff", fontFamily: '"Lexend Exa", sans-serif', fontSize: "18px", letterSpacing: ".08em", cursor: "pointer", boxShadow: "4px 4px 0 #000" }}
          >
            {loading ? "VERIFYING..." : "VERIFY EMAIL"}
          </button>
        </form>

        <button
          type="button"
          onClick={handleResend}
          style={{ marginTop: "1rem", width: "100%", padding: "0.9rem 1rem", border: "2px solid #000", background: "#FFF6EA", color: "#000", fontFamily: '"Lexend Exa", sans-serif', fontSize: "16px", letterSpacing: ".08em", cursor: "pointer", boxShadow: "4px 4px 0 #000" }}
        >
          RESEND OTP
        </button>
      </div>
    </main>
  );
}

export default VerifyEmail;
