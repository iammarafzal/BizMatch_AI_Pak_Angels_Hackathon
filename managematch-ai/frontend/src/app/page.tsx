import Link from "next/link";
import { ArrowRight, BarChart2, ShieldCheck, Users } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-obsidian text-slate-100 font-sans selection:bg-emerald-500/30">
      {/* Header */}
      <header className="border-b border-white/10 bg-obsidian/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-400 to-cyan-500 flex items-center justify-center font-bold text-obsidian">M</div>
            <span className="font-semibold text-lg tracking-tight text-white">ManageMatch AI</span>
          </div>
          <nav className="hidden md:flex gap-6 text-sm font-medium text-slate-400">
            <Link href="#how-it-works" className="hover:text-emerald-400 transition-colors">How it Works</Link>
            <Link href="#features" className="hover:text-emerald-400 transition-colors">Features</Link>
            <a href="https://github.com/iammarafzal/BizMatch_AI_Pak_Angels_Hackathon" target="_blank" rel="noreferrer" className="hover:text-emerald-400 transition-colors">Source Code</a>
          </nav>
          <div className="flex items-center gap-4">
            <Link 
              href="/onboarding" 
              className="bg-emerald-500 hover:bg-emerald-400 text-obsidian px-4 py-2 rounded-md font-semibold text-sm transition-all"
            >
              Get Started
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <main className="max-w-7xl mx-auto px-6 pt-24 pb-16 md:pt-32 md:pb-24">
        <div className="max-w-3xl mx-auto text-center space-y-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-semibold uppercase tracking-wider border border-emerald-500/20">
            <ShieldCheck className="w-4 h-4" />
            Pak Angels Hackathon MVP
          </div>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-200 to-slate-400">
            Find the Manager Your Business Actually Needs.
          </h1>
          <p className="text-lg md:text-xl text-slate-400 leading-relaxed max-w-2xl mx-auto">
            Stop guessing on executive hires. Our hybrid deterministic scoring and Gemini AI engine analyzes your exact startup context to find mathematically backed, highly-qualified operational leaders.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link 
              href="/onboarding"
              className="w-full sm:w-auto flex items-center justify-center gap-2 bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-obsidian px-8 py-4 rounded-lg font-bold text-lg transition-all shadow-lg shadow-emerald-500/20 hover:shadow-emerald-500/40"
            >
              Find My Manager <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>

        {/* Value Props */}
        <div className="grid md:grid-cols-3 gap-8 mt-24" id="features">
          <div className="bg-white/5 border border-white/10 p-8 rounded-2xl hover:bg-white/10 transition-colors">
            <div className="w-12 h-12 rounded-lg bg-emerald-500/20 flex items-center justify-center text-emerald-400 mb-6">
              <BarChart2 className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-3">Deterministic Scoring</h3>
            <p className="text-slate-400 leading-relaxed">
              No black-box LLM matching. We use a transparent 6-factor mathematical engine to rank candidates based on industry, stage, skills, and budget overlap.
            </p>
          </div>
          
          <div className="bg-white/5 border border-white/10 p-8 rounded-2xl hover:bg-white/10 transition-colors">
            <div className="w-12 h-12 rounded-lg bg-cyan-500/20 flex items-center justify-center text-cyan-400 mb-6">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-3">Anti-Hallucination Audit</h3>
            <p className="text-slate-400 leading-relaxed">
              LangGraph validation nodes strip away unverified skills. If a manager doesn&apos;t explicitly have the experience in their profile, it&apos;s flagged as a missing requirement.
            </p>
          </div>

          <div className="bg-white/5 border border-white/10 p-8 rounded-2xl hover:bg-white/10 transition-colors">
            <div className="w-12 h-12 rounded-lg bg-violet-500/20 flex items-center justify-center text-violet-400 mb-6">
              <Users className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-3">Explainable Trade-offs</h3>
            <p className="text-slate-400 leading-relaxed">
              Every match comes with a Gemini-powered qualitative deep dive highlighting strategic synergies and potential risks, so you make the final informed decision.
            </p>
          </div>
        </div>
      </main>

      <footer className="border-t border-white/10 py-12 text-center text-slate-500 text-sm">
        <p>Built for the Pak Angels Hackathon. Powered by FastAPI, Next.js, and Google Gemini.</p>
      </footer>
    </div>
  );
}
