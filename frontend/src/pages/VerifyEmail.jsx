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
    <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", background: "#0f172a", color: "#fff" }}>
      <div style={{ width: "100%", maxWidth: "430px", background: "#111827", padding: "2rem", borderRadius: "16px", boxShadow: "0 12px 32px rgba(0,0,0,0.25)" }}>
        <h1 style={{ marginBottom: "1rem", textAlign: "center" }}>Verify email</h1>

        <form onSubmit={handleVerify} style={{ display: "grid", gap: "1rem" }}>
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="Enter your email"
            required
            style={{ padding: "0.9rem 1rem", borderRadius: "10px", border: "1px solid #374151", background: "#1f2937", color: "#fff" }}
          />

          <input
            type="text"
            value={code}
            onChange={(event) => setCode(event.target.value)}
            placeholder="6-digit verification code"
            required
            style={{ padding: "0.9rem 1rem", borderRadius: "10px", border: "1px solid #374151", background: "#1f2937", color: "#fff" }}
          />

          {message && <div style={{ color: "#86efac" }}>{message}</div>}
          {error && <div style={{ color: "#fca5a5" }}>{error}</div>}

          <button
            type="submit"
            disabled={loading}
            style={{ padding: "0.9rem 1rem", borderRadius: "10px", border: "none", background: "#38bdf8", color: "#082f49", fontWeight: 700, cursor: "pointer" }}
          >
            {loading ? "Verifying..." : "Verify email"}
          </button>
        </form>

        <button
          type="button"
          onClick={handleResend}
          style={{ marginTop: "1rem", width: "100%", padding: "0.8rem 1rem", borderRadius: "10px", border: "1px solid #374151", background: "transparent", color: "#fff", cursor: "pointer" }}
        >
          Resend OTP
        </button>
      </div>
    </main>
  );
}

export default VerifyEmail;
