"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import type { JobMatch, ResumeData, UploadResponse } from "@/lib/api";

export default function DashboardPage() {
  const router = useRouter();
  const [data, setData] = useState<UploadResponse | null>(null);
  const [activeJob, setActiveJob] = useState<JobMatch | null>(null);
  const [filter, setFilter] = useState<"all" | "remote" | "full-time" | "contract">("all");

  useEffect(() => {
    const raw = sessionStorage.getItem("jobmatch_result");
    if (!raw) { router.push("/"); return; }
    try {
      const parsed = JSON.parse(raw) as UploadResponse;
      setData(parsed);
      if (parsed.matches?.length) setActiveJob(parsed.matches[0]);
    } catch { router.push("/"); }
  }, [router]);

  if (!data) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100vh", background: "#f8fafc" }}>
      <div style={{ width: "36px", height: "36px", border: "3px solid #e2e8f0", borderTopColor: "#2563eb", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
    </div>
  );

  const { resume, matches } = data;

  const filteredMatches = matches.filter(job => {
    if (filter === "all") return true;
    const jt = (job.job_type || "").toLowerCase();
    if (filter === "remote") return jt.includes("remote");
    if (filter === "full-time") return jt.includes("full");
    if (filter === "contract") return jt.includes("contract");
    return true;
  });

  const scoreColor = (s: number) => s >= 75 ? "#16a34a" : s >= 55 ? "#d97706" : "#dc2626";
  const scoreBg = (s: number) => s >= 75 ? "#f0fdf4" : s >= 55 ? "#fffbeb" : "#fff1f2";
  const getApplyUrl = (job: JobMatch) => job.apply_url || job.indeed_apply_url || job.linkedin_apply_url || "#";
  const hasApply = (job: JobMatch) => !!(job.apply_url || job.indeed_apply_url || job.linkedin_apply_url);

  return (
    <div style={{ display: "flex", height: "100vh", overflow: "hidden", background: "#f8fafc", fontFamily: "'DM Sans', sans-serif" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700;9..40,800;9..40,900&display=swap');
        @keyframes spin { to { transform: rotate(360deg); } }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 99px; }
        .score-bar { height: 6px; border-radius: 99px; background: #f1f5f9; overflow: hidden; }
        .score-bar-fill { height: 100%; border-radius: 99px; transition: width 0.8s cubic-bezier(0.16,1,0.3,1); }
        .tag { display: inline-flex; align-items: center; padding: 3px 10px; border-radius: 99px; font-size: 11px; font-weight: 600; }
        .tag-skill { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
        .tag-missing { background: #fff1f2; color: #e11d48; border: 1px solid #fecdd3; }
        .djcard:hover { background: #f0f7ff !important; border-color: #93c5fd !important; }
        .djcard { transition: all 0.15s; }
        .nav-btn:hover { background: #f1f5f9 !important; }
        .apply-btn:hover { opacity: 0.88; }
        a { text-decoration: none; }
      `}</style>

      {/* ══ SIDEBAR ══ */}
      <aside style={{ width: "276px", flexShrink: 0, height: "100vh", overflowY: "auto", borderRight: "1px solid #e2e8f0", background: "#fff", padding: "24px 16px", display: "flex", flexDirection: "column", gap: "20px" }}>

        {/* Top nav bar inside sidebar */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
          <div style={{ width: "30px", height: "30px", borderRadius: "8px", background: "linear-gradient(135deg,#2563eb,#7c3aed)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
            <svg width="13" height="13" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="9" stroke="white" strokeWidth="2"/><circle cx="10" cy="10" r="4" fill="white"/></svg>
          </div>
          <span style={{ fontWeight: 900, fontSize: "17px", color: "#0f0f0f", letterSpacing: "-0.03em" }}>JobMatch</span>
        </div>

        {/* Profile card */}
        <div style={{ padding: "16px", borderRadius: "14px", background: "#f8fafc", border: "1px solid #f1f5f9" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "14px" }}>
            <div style={{ width: "46px", height: "46px", borderRadius: "50%", background: "linear-gradient(135deg,#2563eb,#7c3aed)", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800, fontSize: "18px", color: "white", flexShrink: 0 }}>
              {(resume.name || "?")[0].toUpperCase()}
            </div>
            <div>
              <p style={{ fontWeight: 800, fontSize: "14px", color: "#0f0f0f", letterSpacing: "-0.01em" }}>{resume.name || "Anonymous"}</p>
              <p style={{ fontSize: "12px", color: "#6b7280", marginTop: "2px" }}>{resume.current_title || "Professional"}</p>
            </div>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
            {resume.location && (
              <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px", color: "#6b7280" }}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
                {resume.location}
              </div>
            )}
            {resume.years_experience != null && (
              <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px", color: "#6b7280" }}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2"/></svg>
                {resume.years_experience}y experience
              </div>
            )}
            <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px", color: "#6b7280" }}>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              {resume.seniority_level || "mid"} level
            </div>
          </div>
        </div>

        {/* Skills */}
        {(resume.technical_skills ?? []).length > 0 && (
          <div>
            <p style={{ fontSize: "11px", fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase", color: "#9ca3af", marginBottom: "10px" }}>Top Skills</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
              {(resume.technical_skills ?? []).slice(0, 10).map(s => (
                <span key={s} className="tag tag-skill">{s}</span>
              ))}
            </div>
          </div>
        )}

        {/* Stats */}
        <div>
          <p style={{ fontSize: "11px", fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase", color: "#9ca3af", marginBottom: "10px" }}>Search Stats</p>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "8px" }}>
            {[
              { val: data.total_jobs_searched?.toString() || "—", label: "Scanned" },
              { val: matches.length.toString(), label: "Matches" },
              { val: matches[0] ? `${matches[0].overall_score}%` : "—", label: "Best Fit", color: matches[0] ? scoreColor(matches[0].overall_score) : "#6b7280" },
            ].map(stat => (
              <div key={stat.label} style={{ padding: "12px 8px", borderRadius: "10px", background: "#f8fafc", border: "1px solid #f1f5f9", display: "flex", flexDirection: "column", alignItems: "center", gap: "3px" }}>
                <span style={{ fontWeight: 800, fontSize: "17px", color: stat.color || "#0f0f0f", letterSpacing: "-0.02em" }}>{stat.val}</span>
                <span style={{ fontSize: "10px", color: "#9ca3af", textAlign: "center" }}>{stat.label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Nav items */}
        <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
          {[
            { icon: "🏠", label: "Dashboard", active: true },
            { icon: "💼", label: "Saved Jobs", active: false },
            { icon: "📄", label: "My Resume", active: false },
            { icon: "⚙️", label: "Settings", active: false },
          ].map(item => (
            <button key={item.label} className="nav-btn" style={{
              display: "flex", alignItems: "center", gap: "10px", padding: "9px 12px",
              borderRadius: "10px", border: "none", cursor: "pointer", textAlign: "left",
              background: item.active ? "#eff6ff" : "transparent",
              color: item.active ? "#2563eb" : "#374151",
              fontSize: "14px", fontWeight: item.active ? 700 : 500,
              fontFamily: "'DM Sans',sans-serif",
              transition: "background 0.15s",
            }}>
              <span>{item.icon}</span>{item.label}
            </button>
          ))}
        </div>

        {/* New search */}
        <button
          onClick={() => { sessionStorage.removeItem("jobmatch_result"); router.push("/"); }}
          style={{ marginTop: "auto", display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", padding: "10px", borderRadius: "10px", background: "transparent", border: "1px solid #e2e8f0", color: "#6b7280", fontSize: "13px", fontFamily: "'DM Sans',sans-serif", fontWeight: 600, cursor: "pointer", transition: "all 0.15s" }}
          onMouseEnter={e => { (e.currentTarget as HTMLElement).style.borderColor = "#2563eb"; (e.currentTarget as HTMLElement).style.color = "#2563eb"; }}
          onMouseLeave={e => { (e.currentTarget as HTMLElement).style.borderColor = "#e2e8f0"; (e.currentTarget as HTMLElement).style.color = "#6b7280"; }}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
          New Search
        </button>
      </aside>

      {/* ══ JOB LIST ══ */}
      <main style={{ flex: "0 0 400px", height: "100vh", overflowY: "auto", borderRight: "1px solid #e2e8f0", display: "flex", flexDirection: "column", background: "#fff" }}>
        {/* Header */}
        <div style={{ padding: "24px 20px 16px", borderBottom: "1px solid #f1f5f9", background: "#fff", position: "sticky", top: 0, zIndex: 5 }}>
          <h1 style={{ fontWeight: 900, fontSize: "22px", letterSpacing: "-0.03em", color: "#0f0f0f", marginBottom: "4px" }}>Your Matches</h1>
          <p style={{ fontSize: "13px", color: "#9ca3af" }}>{filteredMatches.length} jobs ranked by AI fit score</p>
          {/* Filters */}
          <div style={{ display: "flex", gap: "6px", marginTop: "14px" }}>
            {(["all", "remote", "full-time", "contract"] as const).map(f => (
              <button key={f} onClick={() => setFilter(f)} style={{
                padding: "5px 14px", borderRadius: "99px", border: "none", cursor: "pointer",
                background: filter === f ? "#eff6ff" : "#f8fafc",
                color: filter === f ? "#2563eb" : "#6b7280",
                fontSize: "12px", fontWeight: filter === f ? 700 : 500,
                fontFamily: "'DM Sans',sans-serif",
                outline: filter === f ? "1.5px solid #bfdbfe" : "1.5px solid transparent",
                transition: "all 0.15s",
              }}>{f === "all" ? "All" : f.charAt(0).toUpperCase() + f.slice(1)}</button>
            ))}
          </div>
        </div>

        {/* Cards */}
        <div style={{ flex: 1, padding: "12px", display: "flex", flexDirection: "column", gap: "8px" }}>
          {filteredMatches.length === 0 ? (
            <div style={{ padding: "40px", textAlign: "center", color: "#9ca3af", fontSize: "14px" }}>No jobs match this filter.</div>
          ) : filteredMatches.map((job, i) => (
            <div key={job.id} className="djcard" onClick={() => setActiveJob(job)} style={{
              padding: "14px 16px", borderRadius: "14px",
              background: activeJob?.id === job.id ? "#eff6ff" : "#fff",
              border: activeJob?.id === job.id ? "1.5px solid #93c5fd" : "1.5px solid #f1f5f9",
              cursor: "pointer", display: "flex", alignItems: "center", gap: "12px", position: "relative",
            }}>
              {/* Rank */}
              <div style={{ position: "absolute", top: "8px", right: "10px", fontSize: "10px", fontWeight: 700, color: "#d1d5db" }}>#{i + 1}</div>

              {/* Score ring */}
              <div style={{ position: "relative", flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
                <svg width="52" height="52" viewBox="0 0 52 52">
                  <circle cx="26" cy="26" r="22" fill="none" stroke="#f1f5f9" strokeWidth="3.5" />
                  <circle cx="26" cy="26" r="22" fill="none" stroke={scoreColor(job.overall_score)} strokeWidth="3.5"
                    strokeDasharray={`${(job.overall_score / 100) * 138.2} 138.2`}
                    strokeDashoffset="34.6" strokeLinecap="round" transform="rotate(-90 26 26)" />
                </svg>
                <span style={{ position: "absolute", fontWeight: 800, fontSize: "11px", color: scoreColor(job.overall_score) }}>{job.match_percentage}%</span>
              </div>

              <div style={{ flex: 1, minWidth: 0 }}>
                <p style={{ fontWeight: 800, fontSize: "14px", color: "#0f0f0f", letterSpacing: "-0.01em", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{job.title}</p>
                <p style={{ fontSize: "12px", color: "#6b7280", marginTop: "2px" }}>{job.company}</p>
                <div style={{ display: "flex", gap: "6px", marginTop: "6px", flexWrap: "wrap", alignItems: "center" }}>
                  <span style={{ fontSize: "11px", color: "#9ca3af" }}>{job.location}</span>
                  {job.salary && <span style={{ fontSize: "11px", color: "#9ca3af" }}>· {job.salary}</span>}
                  <span style={{
                    padding: "2px 8px", borderRadius: "99px", fontSize: "10px", fontWeight: 600,
                    background: job.job_type?.toLowerCase().includes("remote") ? "#f0fdf4" : "#f8fafc",
                    color: job.job_type?.toLowerCase().includes("remote") ? "#16a34a" : "#6b7280",
                    border: job.job_type?.toLowerCase().includes("remote") ? "1px solid #bbf7d0" : "1px solid #e2e8f0",
                  }}>{job.job_type || "Full-time"}</span>
                </div>
              </div>

              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#d1d5db" strokeWidth="2"><polyline points="9 18 15 12 9 6"/></svg>
            </div>
          ))}
        </div>
      </main>

      {/* ══ DETAIL PANEL ══ */}
      {activeJob && (
        <aside style={{ flex: 1, height: "100vh", overflowY: "auto", display: "flex", flexDirection: "column", background: "#fff" }}>
          {/* Header */}
          <div style={{ padding: "28px 28px 20px", borderBottom: "1px solid #f1f5f9", background: "#fff", position: "sticky", top: 0, zIndex: 5 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "16px", marginBottom: "18px" }}>
              <div>
                <h2 style={{ fontWeight: 900, fontSize: "22px", color: "#0f0f0f", letterSpacing: "-0.03em", lineHeight: 1.2 }}>{activeJob.title}</h2>
                <p style={{ fontSize: "14px", color: "#6b7280", marginTop: "4px" }}>{activeJob.company}</p>
              </div>
              <div style={{
                padding: "8px 16px", borderRadius: "99px", fontWeight: 800, fontSize: "18px",
                color: scoreColor(activeJob.overall_score),
                background: scoreBg(activeJob.overall_score),
                border: `1px solid ${scoreColor(activeJob.overall_score)}33`,
                flexShrink: 0,
              }}>{activeJob.overall_score}%</div>
            </div>

            {/* Apply buttons */}
            <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
              {hasApply(activeJob) ? (
                <>
                  <a href={getApplyUrl(activeJob)} target="_blank" rel="noopener noreferrer" className="apply-btn"
                    style={{ display: "inline-flex", alignItems: "center", gap: "6px", padding: "10px 22px", borderRadius: "8px", background: "#2563eb", color: "white", fontFamily: "'DM Sans',sans-serif", fontWeight: 700, fontSize: "14px", transition: "opacity 0.15s" }}>
                    Apply Now
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6M15 3h6v6M10 14L21 3"/></svg>
                  </a>
                  {activeJob.indeed_apply_url && (
                    <a href={activeJob.indeed_apply_url} target="_blank" rel="noopener noreferrer"
                      style={{ display: "inline-flex", alignItems: "center", padding: "10px 18px", borderRadius: "8px", border: "1.5px solid #e2e8f0", color: "#374151", fontFamily: "'DM Sans',sans-serif", fontWeight: 600, fontSize: "13px" }}>
                      Indeed
                    </a>
                  )}
                  {activeJob.linkedin_apply_url && (
                    <a href={activeJob.linkedin_apply_url} target="_blank" rel="noopener noreferrer"
                      style={{ display: "inline-flex", alignItems: "center", padding: "10px 18px", borderRadius: "8px", border: "1.5px solid #e2e8f0", color: "#374151", fontFamily: "'DM Sans',sans-serif", fontWeight: 600, fontSize: "13px" }}>
                      LinkedIn
                    </a>
                  )}
                </>
              ) : (
                <span style={{ fontSize: "13px", color: "#9ca3af", fontStyle: "italic" }}>Apply link not available for this listing</span>
              )}
            </div>
          </div>

          {/* Body */}
          <div style={{ padding: "24px 28px", display: "flex", flexDirection: "column", gap: "28px" }}>

            {/* Score breakdown */}
            <div>
              <p style={{ fontSize: "11px", fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase", color: "#9ca3af", marginBottom: "16px" }}>Match Breakdown</p>
              {[
                { label: "Semantic Fit", value: activeJob.semantic_score },
                { label: "Skill Match", value: activeJob.skill_match_score },
                { label: "Experience", value: activeJob.experience_score },
                { label: "Location", value: activeJob.location_score },
              ].map(row => (
                <div key={row.label} style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "10px" }}>
                  <span style={{ fontSize: "13px", color: "#6b7280", width: "110px", flexShrink: 0 }}>{row.label}</span>
                  <div style={{ flex: 1, display: "flex", alignItems: "center", gap: "10px" }}>
                    <div className="score-bar" style={{ flex: 1 }}>
                      <div className="score-bar-fill" style={{ width: `${row.value}%`, background: scoreColor(row.value) }} />
                    </div>
                    <span style={{ fontWeight: 700, fontSize: "13px", color: scoreColor(row.value), width: "38px", textAlign: "right" }}>{row.value}%</span>
                  </div>
                </div>
              ))}
            </div>

            {/* AI Analysis */}
            {activeJob.explanation && (
              <div>
                <p style={{ fontSize: "11px", fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase", color: "#9ca3af", marginBottom: "12px", display: "flex", alignItems: "center", gap: "6px" }}>
                  <span style={{ color: "#2563eb", fontSize: "14px" }}>◈</span> AI Analysis
                </p>
                <p style={{ fontSize: "14px", color: "#374151", lineHeight: 1.72, padding: "14px 16px", borderRadius: "10px", background: "#eff6ff", border: "1px solid #bfdbfe" }}>{activeJob.explanation}</p>
              </div>
            )}

            {/* Matched skills */}
            {activeJob.matched_skills?.length > 0 && (
              <div>
                <p style={{ fontSize: "11px", fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase", color: "#9ca3af", marginBottom: "12px" }}>Matched Skills</p>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                  {activeJob.matched_skills.map(s => <span key={s} className="tag tag-skill">{s}</span>)}
                </div>
              </div>
            )}

            {/* Missing skills */}
            {activeJob.missing_skills?.length > 0 && (
              <div>
                <p style={{ fontSize: "11px", fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase", color: "#9ca3af", marginBottom: "12px" }}>Skills to Develop</p>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                  {activeJob.missing_skills.map(s => <span key={s} className="tag tag-missing">{s}</span>)}
                </div>
              </div>
            )}

            {/* Description */}
            {activeJob.description && (
              <div>
                <p style={{ fontSize: "11px", fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase", color: "#9ca3af", marginBottom: "12px" }}>About the Role</p>
                <p style={{ fontSize: "14px", color: "#4b5563", lineHeight: 1.75 }}>
                  {activeJob.description.length > 600 ? activeJob.description.slice(0, 600) + "…" : activeJob.description}
                </p>
              </div>
            )}

            {/* Job meta */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
              {[
                { label: "Location", value: activeJob.location },
                { label: "Job Type", value: activeJob.job_type || "Full-time" },
                { label: "Salary", value: activeJob.salary || "Not disclosed" },
                { label: "Source", value: activeJob.source || "—" },
              ].map(m => (
                <div key={m.label} style={{ padding: "12px 14px", borderRadius: "10px", background: "#f8fafc", border: "1px solid #f1f5f9" }}>
                  <p style={{ fontSize: "11px", color: "#9ca3af", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "4px" }}>{m.label}</p>
                  <p style={{ fontSize: "13px", fontWeight: 700, color: "#0f0f0f" }}>{m.value}</p>
                </div>
              ))}
            </div>

            {activeJob.source === "demo" && (
              <div style={{ padding: "10px 14px", borderRadius: "10px", background: "#fffbeb", border: "1px solid #fde68a", color: "#92400e", fontSize: "12px" }}>
                Demo data shown — connect the Mantiks API for live listings.
              </div>
            )}
          </div>
        </aside>
      )}
    </div>
  );
}