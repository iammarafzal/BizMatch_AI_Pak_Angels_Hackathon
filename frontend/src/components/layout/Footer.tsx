import Link from "next/link";
import { ShieldCheck } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white text-slate-600 mt-auto">
      {/* Responsible AI Advisory Disclaimer Banner */}
      <div className="border-b border-slate-200 bg-slate-50 py-3.5 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-center gap-2.5 text-center sm:text-left">
          <div className="p-1 rounded-md bg-indigo-50 border border-indigo-200 text-indigo-700 shrink-0">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <p className="text-xs text-slate-600 max-w-4xl leading-relaxed">
            <strong className="text-slate-800 font-semibold">Decision Support Advisory:</strong>{" "}
            BizMatch AI is an AI-powered decision-support platform. Recommendations provide advisory trade-off analysis; final hiring choices remain with the founder.
          </p>
        </div>
      </div>

      {/* Main Footer Links & Copyright */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-slate-500">
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded bg-indigo-600 text-white flex items-center justify-center text-[10px] font-bold">
            B
          </div>
          <span className="text-slate-700 font-semibold">BizMatch AI</span>
          <span>•</span>
          <span>Pak Angels Hackathon MVP</span>
        </div>

        <div className="flex flex-wrap items-center gap-6">
          <Link href="/match" className="hover:text-indigo-600 transition-colors">
            Needs Assessment
          </Link>
          <Link href="/match?demo=true" className="hover:text-indigo-600 transition-colors">
            FashionCart Demo
          </Link>
          <a
            href="https://github.com/iammarafzal/BizMatch_AI_Pak_Angels_Hackathon"
            target="_blank"
            rel="noreferrer"
            className="hover:text-indigo-600 transition-colors flex items-center gap-1.5"
          >
            <span>GitHub Repository</span>
          </a>
        </div>

        <div>
          <p>© {new Date().getFullYear()} BizMatch AI. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
