"use client";

import { useState, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import { uploadResume, type UploadResponse } from "@/lib/api";

export default function LandingPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStage, setUploadStage] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);

  const STAGES = [
    "Reviewing your resume...",
    "Finding matching roles...",
    "Ranking by fit...",
    "Personalising results...",
    "Almost done...",
    "Complete!",
  ];

  const handleFile = useCallback(async (file: File) => {
    const ext = file.name.split(".").pop()?.toLowerCase();
    if (!["pdf","doc","docx","png","jpg","jpeg","webp","bmp","tiff","tif"].includes(ext || "")) {
      setError("Please upload a PDF, DOCX, or image file.");
      return;
    }
    if (file.size > 15 * 1024 * 1024) { setError("File must be under 15MB."); return; }
    setError(null); setIsUploading(true); setProgress(0);
    let idx = 0; setUploadStage(STAGES[0]);
    const t = setInterval(() => {
      idx = Math.min(idx + 1, STAGES.length - 1);
      setUploadStage(STAGES[idx]);
      setProgress(Math.round((idx / (STAGES.length - 1)) * 85));
    }, 2800);
    try {
      const result: UploadResponse = await uploadResume(file);
      clearInterval(t); setProgress(100); setUploadStage("Complete!");
      sessionStorage.setItem("jobmatch_result", JSON.stringify(result));
      await new Promise(r => setTimeout(r, 400));
      router.push("/dashboard");
    } catch (e: any) {
      clearInterval(t); setIsUploading(false); setProgress(0); setUploadStage("");
      setError(e.message || "Upload failed. Please try again.");
    }
  }, [router]);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  }, [handleFile]);

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) handleFile(f);
  };

  const FloatCard = ({ logo, logoStyle, title, sub }: { logo: string; logoStyle: React.CSSProperties; title: string; sub: string }) => (
    <div style={{ background: "#fff", borderRadius: "14px", padding: "12px 16px", display: "flex", alignItems: "center", gap: "10px", boxShadow: "0 8px 32px rgba(0,0,0,0.25)", width: "100%" }}>
      <div style={{ width: "38px", height: "38px", borderRadius: "9px", display: "flex", alignItems: "center", justifyContent: "center", color: "white", fontWeight: 900, fontSize: "14px", flexShrink: 0, ...logoStyle }}>{logo}</div>
      <div>
        <div style={{ fontSize: "13px", fontWeight: 700, color: "#0f0f0f", letterSpacing: "-0.01em" }}>{title}</div>
        <div style={{ fontSize: "11px", color: "#6b7280", fontWeight: 500, marginTop: "1px" }}>{sub}</div>
      </div>
    </div>
  );

  return (
    <div style={{ fontFamily: "'Manrope', sans-serif", background: "#fff", minHeight: "100vh" }}>

      {/* FONT IMPORT + GLOBAL STYLES */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800;900&display=swap');
        @keyframes spin { to { transform: rotate(360deg); } }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        input::placeholder { color: #9ca3af; }
        a:hover { opacity: 0.8; }
      `}</style>

      {/* ── NAV ── */}
      <div style={{ background: "#0a0a14", position: "sticky", top: 0, zIndex: 100, borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
        <nav style={{ maxWidth: "1200px", margin: "0 auto", display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 40px", height: "64px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", fontWeight: 800, fontSize: "19px", color: "#fff", letterSpacing: "-0.03em" }}>
            <div style={{ width: "30px", height: "30px", borderRadius: "8px", background: "linear-gradient(135deg,#6366f1,#8b5cf6)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <svg width="13" height="13" viewBox="0 0 16 16" fill="none"><path d="M8 1L9.8 6.2H15.3L10.8 9.4L12.5 14.6L8 11.3L3.5 14.6L5.2 9.4L0.7 6.2H6.2L8 1Z" fill="white"/></svg>
            </div>
            JobMatch
          </div>
          <div style={{ display: "flex", gap: "4px" }}>
            {["Find Jobs", "Companies", "Salaries"].map(l => (
              <a key={l} href="#" style={{ fontSize: "14px", color: "rgba(255,255,255,0.6)", textDecoration: "none", fontWeight: 500, padding: "6px 14px", borderRadius: "8px" }}>{l}</a>
            ))}
          </div>
          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            <a href="#" style={{ fontSize: "14px", color: "rgba(255,255,255,0.6)", fontWeight: 500, padding: "6px 14px", textDecoration: "none" }}>Sign In</a>
            <button onClick={() => fileInputRef.current?.click()} style={{ padding: "8px 20px", borderRadius: "99px", background: "#fff", color: "#0f0f0f", fontSize: "13px", fontWeight: 700, border: "none", cursor: "pointer", fontFamily: "'Manrope',sans-serif", letterSpacing: "-0.01em" }}>
              Upload Resume
            </button>
          </div>
        </nav>
      </div>

      {/* ── HERO ── */}
      <div style={{ background: "#0a0a14", position: "relative", overflow: "hidden" }}>
        {/* Background glows */}
        <div style={{ position: "absolute", top: "-200px", left: "-200px", width: "600px", height: "600px", borderRadius: "50%", background: "radial-gradient(circle,rgba(99,102,241,0.2) 0%,transparent 65%)", pointerEvents: "none" }} />
        <div style={{ position: "absolute", bottom: "-100px", right: "-100px", width: "500px", height: "500px", borderRadius: "50%", background: "radial-gradient(circle,rgba(139,92,246,0.15) 0%,transparent 65%)", pointerEvents: "none" }} />
        <div style={{ position: "absolute", inset: 0, backgroundImage: "linear-gradient(rgba(255,255,255,0.025) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,0.025) 1px,transparent 1px)", backgroundSize: "60px 60px", pointerEvents: "none" }} />

        {/* 3-column layout: cards | center | cards */}
        <div style={{ maxWidth: "1280px", margin: "0 auto", padding: "80px 40px", display: "grid", gridTemplateColumns: "220px 1fr 220px", gap: "40px", alignItems: "center", position: "relative", zIndex: 2 }}>

          {/* LEFT CARDS */}
          <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
            <FloatCard logo="in" logoStyle={{ background: "linear-gradient(135deg,#405de6,#833ab4)" }} title="LinkedIn" sub="Hiring Design Manager" />
            <FloatCard logo="S" logoStyle={{ background: "#635bff" }} title="Stripe" sub="Open 12 Jobs!" />
          </div>

          {/* CENTER — headline + search */}
          <div style={{ textAlign: "center" }}>
            <div style={{ display: "inline-flex", alignItems: "center", gap: "7px", padding: "5px 14px 5px 8px", borderRadius: "99px", background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.1)", fontSize: "12px", color: "rgba(255,255,255,0.65)", fontWeight: 600, marginBottom: "28px", letterSpacing: "0.02em" }}>
              <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "#34d399", boxShadow: "0 0 8px #34d399", display: "inline-block" }} />
              Matched to your profile
            </div>

            <h1 style={{ fontSize: "clamp(44px,5.5vw,72px)", fontWeight: 900, lineHeight: 1.03, letterSpacing: "-0.04em", color: "#fff", marginBottom: "18px" }}>
              Best Platform To<br />Get Your{" "}
              <span style={{ background: "linear-gradient(135deg,#818cf8,#c084fc)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
                Dream Job
              </span>
            </h1>

            <p style={{ fontSize: "16px", color: "rgba(255,255,255,0.45)", lineHeight: 1.65, marginBottom: "40px", maxWidth: "420px", margin: "0 auto 40px", fontWeight: 400 }}>
              More than 554,000 jobs listed. Upload your resume and get matched instantly.
            </p>

            {/* Search bar */}
            <div style={{ display: "flex", alignItems: "center", background: "#fff", borderRadius: "14px", padding: "7px 7px 7px 20px", gap: "10px", boxShadow: "0 20px 60px rgba(0,0,0,0.45)", marginBottom: "14px" }}>
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
              <input type="text" placeholder="Job title or keyword" style={{ flex: 1, border: "none", outline: "none", fontSize: "14px", fontFamily: "'Manrope',sans-serif", color: "#0f0f0f", fontWeight: 500, background: "transparent", minWidth: 0 }} />
              <div style={{ width: "1px", height: "22px", background: "#e5e7eb", flexShrink: 0 }} />
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2" style={{ flexShrink: 0 }}><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
              <input type="text" placeholder="Location" style={{ flex: 1, border: "none", outline: "none", fontSize: "14px", fontFamily: "'Manrope',sans-serif", color: "#0f0f0f", fontWeight: 500, background: "transparent", minWidth: 0 }} />
              <button style={{ padding: "11px 24px", borderRadius: "10px", background: "#6366f1", color: "#fff", fontSize: "14px", fontWeight: 700, fontFamily: "'Manrope',sans-serif", border: "none", cursor: "pointer", flexShrink: 0 }}>
                Search
              </button>
            </div>

            <p style={{ fontSize: "12px", color: "rgba(255,255,255,0.3)", fontWeight: 500, marginBottom: "32px" }}>
              Popular:{" "}
              <span style={{ color: "rgba(255,255,255,0.55)", fontWeight: 600 }}>Product Designer</span> ·{" "}
              <span style={{ color: "rgba(255,255,255,0.55)", fontWeight: 600 }}>Frontend Engineer</span> ·{" "}
              <span style={{ color: "rgba(255,255,255,0.55)", fontWeight: 600 }}>Data Analyst</span>
            </p>

            {/* Upload strip */}
            <input ref={fileInputRef} type="file" accept=".pdf,.doc,.docx,.png,.jpg,.jpeg,.webp,.bmp,.tiff" style={{ display: "none" }} onChange={onFileChange} />

            {isUploading ? (
              <div style={{ display: "flex", flexDirection: "column" as const, alignItems: "center", gap: "12px", padding: "24px", borderRadius: "16px", background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.07)" }}>
                <div style={{ position: "relative" as const, width: "38px", height: "38px" }}>
                  <div style={{ position: "absolute" as const, inset: 0, borderRadius: "50%", border: "2.5px solid transparent", borderTopColor: "#6366f1", animation: "spin 0.9s linear infinite" }} />
                  <div style={{ position: "absolute" as const, inset: "8px", borderRadius: "50%", border: "2px solid transparent", borderTopColor: "#c084fc", animation: "spin 0.6s linear infinite reverse" }} />
                </div>
                <p style={{ fontSize: "14px", color: "#fff", fontWeight: 600 }}>{uploadStage}</p>
                <div style={{ width: "240px", height: "3px", borderRadius: "99px", background: "rgba(255,255,255,0.08)", overflow: "hidden" }}>
                  <div style={{ height: "100%", width: `${progress}%`, background: "linear-gradient(90deg,#6366f1,#8b5cf6)", borderRadius: "99px", transition: "width 0.6s ease" }} />
                </div>
                <p style={{ fontSize: "11px", color: "rgba(255,255,255,0.35)" }}>{progress}% complete</p>
              </div>
            ) : (
              <div
                onDragOver={e => e.preventDefault()}
                onDrop={onDrop}
                onClick={() => fileInputRef.current?.click()}
                style={{ display: "inline-flex", alignItems: "center", gap: "10px", cursor: "pointer" }}
              >
                <button style={{ padding: "13px 32px", borderRadius: "99px", background: "linear-gradient(135deg,#6366f1,#8b5cf6)", color: "#fff", fontSize: "14px", fontWeight: 700, fontFamily: "'Manrope',sans-serif", border: "none", cursor: "pointer", boxShadow: "0 4px 24px rgba(99,102,241,0.45)", letterSpacing: "-0.01em" }}>
                  Upload Resume & Get Matched →
                </button>
              </div>
            )}
            {error && <p style={{ marginTop: "12px", fontSize: "13px", color: "#f87171", fontWeight: 500 }}>{error}</p>}
          </div>

          {/* RIGHT CARDS */}
          <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
            <FloatCard logo="f" logoStyle={{ background: "#1877f2" }} title="Meta" sub="Open 24 Jobs!" />
            <FloatCard logo="▲" logoStyle={{ background: "#0f172a", fontSize: "12px" }} title="Vercel" sub="Open 8 Jobs!" />
          </div>
        </div>
      </div>

      {/* ── LOGOS ── */}
      <div style={{ borderBottom: "1px solid #f3f4f6", padding: "24px 40px", display: "flex", alignItems: "center", background: "#fafafa" }}>
        <span style={{ fontSize: "11px", color: "#9ca3af", fontWeight: 700, whiteSpace: "nowrap" as const, marginRight: "40px", letterSpacing: "0.08em", textTransform: "uppercase" as const }}>Trusted by</span>
        <div style={{ display: "flex", alignItems: "center", flex: 1, justifyContent: "space-between" as const }}>
          {["Coinbase","Upwork","Stripe","Dropbox","Webflow","Netflix","Figma"].map(n => (
            <span key={n} style={{ fontSize: "15px", fontWeight: 800, color: "#d1d5db", letterSpacing: "-0.03em" }}>{n}</span>
          ))}
        </div>
      </div>

      {/* ── CATEGORIES ── */}
      <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "80px 40px" }}>
        <p style={{ fontSize: "11px", fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase" as const, color: "#9ca3af", marginBottom: "10px" }}>Browse by category</p>
        <h2 style={{ fontSize: "clamp(30px,3.5vw,42px)", fontWeight: 900, letterSpacing: "-0.04em", color: "#0f0f0f", marginBottom: "40px", lineHeight: 1.1 }}>Explore by Categories</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: "16px" }}>
          {[
            { icon: "💻", title: "Engineering", count: "1,240", bg: "#eef2ff", active: false },
            { icon: "🎨", title: "Design", count: "890", bg: "#fdf4ff", active: true },
            { icon: "📊", title: "Marketing", count: "2,510", bg: "#f0fdf4", active: false },
            { icon: "💼", title: "Management", count: "1,310", bg: "#fff7ed", active: false },
            { icon: "⚖️", title: "Legal", count: "620", bg: "#fefce8", active: false },
            { icon: "🏢", title: "Administration", count: "1,100", bg: "#f1f5f9", active: false },
            { icon: "💰", title: "Finance", count: "980", bg: "#f0fdf4", active: false },
            { icon: "📣", title: "Sales", count: "1,450", bg: "#fff1f2", active: false },
          ].map(c => (
            <div key={c.title} style={{ padding: "22px 20px", borderRadius: "14px", border: c.active ? "1.5px solid #6366f1" : "1.5px solid #f3f4f6", background: c.active ? "#eef2ff" : "#fff", cursor: "pointer" }}>
              <div style={{ width: "40px", height: "40px", borderRadius: "10px", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "18px", background: c.bg, marginBottom: "12px" }}>{c.icon}</div>
              <div style={{ fontSize: "15px", fontWeight: 800, color: "#0f0f0f", letterSpacing: "-0.02em", marginBottom: "4px" }}>{c.title}</div>
              <div style={{ fontSize: "12px", color: "#6b7280", fontWeight: 500 }}><strong style={{ color: c.active ? "#6366f1" : "#6366f1", fontWeight: 700 }}>{c.count}</strong> Jobs Available</div>
            </div>
          ))}
        </div>
      </div>

      {/* ── FEATURED JOBS ── */}
      <div style={{ background: "#f9fafb", borderTop: "1px solid #f3f4f6", borderBottom: "1px solid #f3f4f6", padding: "80px 40px" }}>
        <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
          <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", marginBottom: "40px" }}>
            <div>
              <p style={{ fontSize: "11px", fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase" as const, color: "#9ca3af", marginBottom: "10px" }}>Hand-picked for you</p>
              <h2 style={{ fontSize: "clamp(28px,3vw,38px)", fontWeight: 900, letterSpacing: "-0.04em", color: "#0f0f0f", lineHeight: 1.1 }}>Featured Job Offer</h2>
            </div>
            <a href="#" style={{ fontSize: "14px", fontWeight: 600, color: "#6366f1", textDecoration: "none" }}>View all →</a>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: "20px" }}>
            {[
              { logo: "N", bg: "#1a1814", company: "Notion", loc: "Remote, Worldwide", title: "Senior Frontend Engineer", type: "Full-time", typeBg: "#f0fdf4", typeColor: "#15803d", typeBorder: "#bbf7d0", salary: "$140k/year", desc: "You will collaborate with the entire team in the company to make a good product that can solve the problem of users.", featured: false },
              { logo: "G", bg: "#fff", logoColor: "#4285F4", company: "Google", loc: "San Francisco, CA", title: "Product Manager", type: "Full-time", typeBg: "#fdf4ff", typeColor: "#7e22ce", typeBorder: "#e9d5ff", salary: "$155k/year", desc: "You will collaborate with the entire team in the company to make a good product that can solve the problem of users.", featured: true },
              { logo: "▲", bg: "#0f172a", company: "Vercel", loc: "Remote, US Only", title: "Product Engineer", type: "Contract", typeBg: "#eff6ff", typeColor: "#1d4ed8", typeBorder: "#bfdbfe", salary: "$125k/year", desc: "You will collaborate with the entire team in the company to make a good product that can solve the problem of users.", featured: false },
              { logo: "in", bg: "linear-gradient(135deg,#405de6,#833ab4)", company: "LinkedIn", loc: "Jakarta, Indonesia", title: "Product Designer", type: "Full-time", typeBg: "#f0fdf4", typeColor: "#15803d", typeBorder: "#bbf7d0", salary: "$145k/year", desc: "You will collaborate with the entire team in the company to make a good product that can solve the problem of users.", featured: false },
              { logo: "Dr", bg: "#ea4c89", company: "Dribbble", loc: "Remote", title: "UI/UX Designer", type: "Full-time", typeBg: "#fff7ed", typeColor: "#c2410c", typeBorder: "#fed7aa", salary: "$120k/year", desc: "You will collaborate with the entire team in the company to make a good product that can solve the problem of users.", featured: false },
              { logo: "Fi", bg: "#f24e1e", company: "Figma", loc: "Bali, Indonesia", title: "UI Designer", type: "Full-time", typeBg: "#f0fdf4", typeColor: "#15803d", typeBorder: "#bbf7d0", salary: "$115k/year", desc: "You will collaborate with the entire team in the company to make a good product that can solve the problem of users.", featured: false },
            ].map((j, i) => (
              <div key={i} style={{ background: "#fff", borderRadius: "18px", border: j.featured ? "1.5px solid #6366f1" : "1.5px solid #f3f4f6", padding: "22px", cursor: "pointer", boxShadow: j.featured ? "0 0 0 1px #6366f1,0 8px 32px rgba(99,102,241,0.12)" : "0 1px 3px rgba(0,0,0,0.04)", transition: "all 0.2s" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "14px" }}>
                  <div style={{ width: "42px", height: "42px", borderRadius: "10px", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 900, fontSize: "14px", color: j.logo === "G" ? "#4285F4" : "#fff", background: j.bg, border: j.logo === "G" ? "1px solid #f3f4f6" : "none", flexShrink: 0 }}>{j.logo}</div>
                  <div>
                    <div style={{ fontSize: "13px", fontWeight: 700, color: "#0f0f0f" }}>{j.company}</div>
                    <div style={{ fontSize: "12px", color: "#9ca3af", fontWeight: 500 }}>{j.loc}</div>
                  </div>
                </div>
                <div style={{ fontSize: "17px", fontWeight: 800, color: "#0f0f0f", letterSpacing: "-0.03em", marginBottom: "4px", lineHeight: 1.25 }}>{j.title}</div>
                <div style={{ fontSize: "12px", color: "#9ca3af", fontWeight: 600, marginBottom: "10px" }}>{j.type}</div>
                <div style={{ fontSize: "13px", color: "#6b7280", lineHeight: 1.65, marginBottom: "16px" }}>{j.desc}</div>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingTop: "14px", borderTop: "1px solid #f3f4f6" }}>
                  <div style={{ fontSize: "15px", fontWeight: 800, color: "#0f0f0f", letterSpacing: "-0.02em" }}>{j.salary}</div>
                  <a href="#" style={{ padding: "7px 18px", borderRadius: "99px", fontSize: "12px", fontWeight: 700, fontFamily: "'Manrope',sans-serif", textDecoration: "none", background: j.featured ? "#6366f1" : "transparent", color: j.featured ? "#fff" : "#6366f1", border: j.featured ? "none" : "1.5px solid #e0e7ff" }}>
                    Apply Now
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── CTA ── */}
      <div style={{ background: "#0a0a14", padding: "80px 40px", position: "relative" as const, overflow: "hidden" }}>
        <div style={{ position: "absolute" as const, top: "-200px", left: "-100px", width: "600px", height: "600px", borderRadius: "50%", background: "radial-gradient(circle,rgba(99,102,241,0.15) 0%,transparent 60%)", pointerEvents: "none" as const }} />
        <div style={{ maxWidth: "1200px", margin: "0 auto", display: "grid", gridTemplateColumns: "1fr auto", gap: "60px", alignItems: "center", position: "relative" as const, zIndex: 1 }}>
          <div>
            <h2 style={{ fontSize: "clamp(32px,4vw,48px)", fontWeight: 900, letterSpacing: "-0.04em", color: "#fff", lineHeight: 1.08, marginBottom: "14px" }}>Stop searching.<br />Start getting hired.</h2>
            <p style={{ fontSize: "16px", color: "rgba(255,255,255,0.4)", lineHeight: 1.65, maxWidth: "440px" }}>Upload your resume once and get matched with roles that fit your background and goals.</p>
          </div>
          <button onClick={() => fileInputRef.current?.click()} style={{ display: "inline-flex", alignItems: "center", gap: "8px", padding: "15px 36px", borderRadius: "99px", background: "#fff", color: "#0f0f0f", fontFamily: "'Manrope',sans-serif", fontWeight: 800, fontSize: "14px", letterSpacing: "-0.02em", border: "none", cursor: "pointer", whiteSpace: "nowrap" as const, boxShadow: "0 4px 24px rgba(0,0,0,0.3)" }}>
            Upload Resume
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </button>
        </div>
      </div>

      {/* ── FOOTER ── */}
      <footer style={{ padding: "32px 40px", display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid #f3f4f6", background: "#fff" }}>
        <div style={{ fontWeight: 800, fontSize: "15px", color: "#0f0f0f", letterSpacing: "-0.03em", display: "flex", alignItems: "center", gap: "7px" }}>
          <div style={{ width: "24px", height: "24px", borderRadius: "6px", background: "linear-gradient(135deg,#6366f1,#8b5cf6)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <svg width="10" height="10" viewBox="0 0 16 16" fill="none"><path d="M8 1L9.8 6.2H15.3L10.8 9.4L12.5 14.6L8 11.3L3.5 14.6L5.2 9.4L0.7 6.2H6.2L8 1Z" fill="white"/></svg>
          </div>
          JobMatch
        </div>
        <div style={{ display: "flex", gap: "24px" }}>
          {["Find Jobs","Privacy","Terms","Contact"].map(l => (
            <a key={l} href="#" style={{ fontSize: "13px", color: "#9ca3af", textDecoration: "none", fontWeight: 500 }}>{l}</a>
          ))}
        </div>
        <span style={{ fontSize: "13px", color: "#d1d5db", fontWeight: 500 }}>© 2026 JobMatch</span>
      </footer>

    </div>
  );
}