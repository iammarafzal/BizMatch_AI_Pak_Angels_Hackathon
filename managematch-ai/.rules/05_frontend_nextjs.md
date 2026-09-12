# Frontend Architecture: Next.js + Tailwind CSS

## 1. Core Responsibilities & Scope
- Build a fast, founder-centric decision-support dashboard.
- Connect exclusively to the FastAPI backend; never import LLM provider SDKs or expose API keys in client code.
- Prioritize demo flow readiness: smooth screen transitions, clear loading animations, and rapid comparison views.

---

## 2. Nine-Screen Architecture & Routes

Organize the user journey into clean Next.js App Router views or a progressive wizard state:

1. `/` (Landing View):
   - Hero: "Find the Manager Your Business Actually Needs"
   - Supporting copy and clear primary CTA button: "Find My Manager"
   - "How It Works" section showing the hybrid AI + deterministic pipeline

2. `/onboarding` (Business Profile & Needs Wizard):
   - Screen 2: Basic Business Info (Name, industry, size, stage, location, employee count)
   - Screen 3: Business Needs (Text areas for goals, operational bottlenecks, required skills, and budget ceiling)
   - Action: "⚡ Load FashionCart Demo" preset button to instantly populate fields for the hackathon demo

3. `/analyzing` (Progressive Loading State):
   - Screen 4: Animated status indicator: "Analyzing business needs & extracting key criteria..."
   - Screen 5: Secondary status indicator: "Evaluating candidate pool against 6 deterministic fit factors..."

4. `/results` (Results & Evaluation Dashboard):
   - Screen 6: Ranked candidate cards (sorted by weighted `overall_score`)
   - Screen 7: Candidate Detail Modal/Drawer showing comprehensive background, salary expectations, and full 6-factor score breakdown
   - Screen 8: AI Decision Card displaying Strengths, Potential Concerns, Missing Requirements, and the Final Verdict
   - Screen 9: Side-by-Side Comparison Matrix for top candidates

---

## 3. Component Hierarchy

```text
frontend/src/
├── app/
│   ├── layout.tsx
│   ├── page.tsx               # Screen 1: Landing
│   ├── match/
│   │   ├── page.tsx           # Screens 2-5: Form & Loading Wizard
│   │   └── results/page.tsx   # Screens 6-9: Results & Deep Dive
├── components/
│   ├── forms/
│   │   ├── BusinessInfoForm.tsx
│   │   └── GoalsAndChallengesForm.tsx
│   ├── dashboard/
│   │   ├── CandidateCard.tsx
│   │   ├── FactorProgressBar.tsx
│   │   ├── AiExplanationCard.tsx
│   │   └── CandidateComparisonTable.tsx
│   └── shared/
│       ├── DemoPresetButton.tsx
│       └── ResponsibleAiBanner.tsx
├── lib/
│   ├── api.ts                 # Typed FastAPI client functions
│   └── types.ts               # Shared TypeScript schemas matching backend models
```

---

## 4. UI/UX & Data Display Specifications

### Factor Breakdown Progress Bars
Render progress bars for all 6 factor scores on each candidate card to ensure complete algorithmic transparency:
- Industry Fit (20% weight)
- Skills Fit (25% weight)
- Experience Fit (20% weight)
- Leadership Fit (15% weight)
- Stage Fit (10% weight)
- Salary Fit (10% weight)

### Score Color Badges
- `85% - 100%`: Green (High Fit)
- `70% - 84%`: Amber (Moderate Fit / Viable Alternative)
- `< 70%`: Slate / Gray (Domain or Budget Mismatch)

### AI Decision Card Scaffolding
- Render four distinct visual sections:
  1. **Strengths** (Green checkmark icons)
  2. **Potential Concerns** (Amber warning icons)
  3. **Missing Requirements** (Gray slash/dash icons)
  4. **Recommendation Verdict** (Highlighted callout card emphasizing trade-offs)

---

## 5. API Integration Layer (`lib/api.ts`)

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export async function analyzeRequirements(payload: {
  name: string;
  industry: string;
  stage: string;
  goals: string;
  challenges: string;
  budget: number;
}) {
  const res = await fetch(`${API_BASE}/analyze-requirements`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function calculateMatches(businessId: string) {
  const res = await fetch(`${API_BASE}/matches/calculate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ business_id: businessId }),
  });
  return res.json();
}

export async function getCandidateExplanation(businessId: string, managerId: string) {
  const res = await fetch(`${API_BASE}/matches/explain`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ business_id: businessId, manager_id: managerId }),
  });
  return res.json();
}
```

## 6. Mandatory Hackathon Guardrails

**One-Click Demo Button**: Include `DemoPresetButton.tsx` at the top of the wizard. Clicking it must instantly populate the inputs with the FashionCart scenario: e-commerce, growth stage, 12 employees, order fulfillment bottlenecks, and $2,000 budget.

**No Mock Hallucinations**: Ensure missing candidate fields render as "Not provided" rather than empty blanks or fabricated credentials.

**Human-in-the-Loop Footer**: Render a permanent footer disclaimer across the dashboard:
*"ManageMatch AI is a decision-support platform. Recommendations provide advisory trade-off analysis; final hiring choices remain with the founder."*