"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Sparkles, ArrowRight, RotateCcw, Shield } from "lucide-react";

export default function Header() {
  const pathname = usePathname();
  const router = useRouter();
  const isInternal = pathname.startsWith("/match") || pathname.startsWith("/results");

  const handleReset = () => {
    if (typeof window !== "undefined") {
      sessionStorage.removeItem("bizmatch_business_data");
      sessionStorage.removeItem("bizmatch_business_payload");
      sessionStorage.removeItem("bizmatch_calculated_matches");
      sessionStorage.removeItem("bizmatch_selected_biz_id");
      sessionStorage.removeItem("bizmatch_analyzed_requirements");
      sessionStorage.removeItem("bizmatch_fallback_active");
      sessionStorage.removeItem("bizmatch_jwt_token");

      try {
        const keysToRemove: string[] = [];
        for (let i = 0; i < sessionStorage.length; i++) {
          const key = sessionStorage.key(i);
          if (key && (key.startsWith("bizmatch_exp_") || key.startsWith("bizmatch_"))) {
            keysToRemove.push(key);
          }
        }
        keysToRemove.forEach((k) => sessionStorage.removeItem(k));
      } catch (err) {
        console.warn("Storage reset warning:", err);
      }
    }
    router.push("/match");
  };

  return (
    <header className="border-b border-slate-200 bg-white/95 backdrop-blur-md sticky top-0 z-40 transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Left: Brand Logo & Executive Tagline */}
        <div className="flex items-center gap-4">
          <Link href="/" className="flex items-center gap-3 group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 rounded-lg p-1">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-bold text-sm shadow-sm group-hover:bg-indigo-700 transition-colors">
              B
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-base tracking-tight text-slate-900 group-hover:text-indigo-600 transition-colors">
                  BizMatch AI
                </span>
                <span className="text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200">
                  Enterprise
                </span>
              </div>
              <span className="text-[11px] text-slate-500 hidden sm:inline-block">
                Executive Manager Decision Support
              </span>
            </div>
          </Link>
        </div>

        {/* Center/Right: Quick Actions */}
        <div className="flex items-center gap-2.5 sm:gap-3">
          {isInternal ? (
            <>
              <button
                type="button"
                onClick={handleReset}
                className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 px-3 sm:px-3.5 py-1.5 text-xs font-semibold transition-all shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                title="Reset all form data and start a new evaluation"
              >
                <RotateCcw className="w-3.5 h-3.5 text-slate-500" />
                <span>New Search / Reset</span>
              </button>

              <Link
                href="/match?demo=true"
                className="hidden sm:inline-flex items-center gap-1.5 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-200 px-3 py-1.5 text-xs font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500"
              >
                <Sparkles className="w-3.5 h-3.5 text-amber-600" />
                <span>⚡ Instant Demo</span>
              </Link>
            </>
          ) : (
            <>
              <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 text-xs font-medium border border-slate-200">
                <Shield className="w-3.5 h-3.5 text-indigo-600" />
                <span>Deterministic Scoring &amp; Gemini AI</span>
              </div>

              <Link
                href="/match?demo=true"
                className="hidden sm:inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 px-3.5 py-2 text-xs font-semibold transition-all shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
              >
                <span>Demo Scenario</span>
              </Link>

              <Link
                href="/match"
                className="flex items-center gap-1.5 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-semibold text-xs transition-all shadow-sm hover:shadow hover:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2"
              >
                <span>Start Assessment</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
