# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Tripforge is an AI-powered travel planner web app.
Tagline: "Forge your perfect journey"
Users input destination, duration, budget, and interests — the app generates a detailed day-by-day itinerary using the Anthropic Claude API.

---

## Tech Stack
- **Framework:** Vite + React 18
- **Language:** TypeScript (.tsx)
- **Styling:** Tailwind CSS
- **Routing:** React Router v6
- **Payments:** Stripe (via Stripe.js)
- **AI:** Anthropic Claude API (calls go through a backend proxy)
- **Backend:** Express.js (Node) — hosted separately or as Hostinger Node app
- **Deployment:** Hostinger (static frontend + Node backend)
- **PDF Export:** jsPDF or html2pdf.js

---

## Project Structure
```
tripforge/
├── public/
│   └── favicon.ico
├── src/
│   ├── main.tsx                  # Entry point
│   ├── App.tsx                   # Router setup
│   ├── pages/
│   │   ├── Landing.tsx           # Landing page
│   │   ├── PlanWizard.tsx        # Multi-step trip form
│   │   └── Result.tsx            # Generated itinerary page
│   ├── components/
│   │   ├── StepForm/
│   │   │   ├── StepDestination.tsx
│   │   │   ├── StepDuration.tsx
│   │   │   ├── StepBudget.tsx
│   │   │   ├── StepInterests.tsx
│   │   │   └── StepTravelers.tsx
│   │   ├── ItineraryCard.tsx     # Single day card
│   │   ├── PaywallOverlay.tsx    # Blur + lock for free users
│   │   ├── LoadingForge.tsx      # Loading animation
│   │   └── PDFExport.tsx         # PDF download button
│   ├── types/
│   │   └── itinerary.ts          # All TypeScript interfaces
│   ├── lib/
│   │   ├── api.ts                # Frontend API calls to backend
│   │   └── stripe.ts             # Stripe.js helper
│   └── styles/
│       └── index.css             # Tailwind imports
├── server/
│   ├── index.ts                  # Express server entry
│   ├── routes/
│   │   ├── generate.ts           # POST /api/generate
│   │   └── payment.ts            # POST /api/payment
│   └── lib/
│       ├── claude.ts             # Claude API helper
│       └── rateLimit.ts          # IP rate limiting
├── .env                          # Environment variables (never commit)
├── .env.example                  # Example env file (commit this)
├── vite.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── CLAUDE.md
```

---

## Environment Variables

### Frontend (.env)
```env
VITE_API_URL=http://localhost:3001
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### Backend (server/.env)
```env
ANTHROPIC_API_KEY=sk-ant-...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=https://tripforge.com
PORT=3001
```

> ⚠️ NEVER expose ANTHROPIC_API_KEY or STRIPE_SECRET_KEY on the frontend.
> All Claude API calls must go through the Express backend.

---

## Routing (React Router v6)
```
/                → Landing.tsx
/plan            → PlanWizard.tsx (multi-step form)
/result/:id      → Result.tsx (generated itinerary)
```

---

## Freemium Logic
| Plan | Price | Features |
|------|-------|----------|
| Free | €0 | Max 3 days shown, no PDF, max 3 generations/day per IP |
| Pay-per-plan | €4.99 | Full plan (up to 14 days), PDF export, shareable link |
| Pro | €9.99/mo | Unlimited plans, PDF export, priority generation |

- Days 4+ are rendered but blurred with `PaywallOverlay.tsx`
- After Stripe payment confirmed → `isPaid` state set to true → full plan visible + PDF button shown
- Rate limit enforced on backend by IP address

---

## Backend API Endpoints

### POST /api/generate
Request:
```json
{
  "destination": "Paris",
  "duration": 7,
  "budget": "mid-range",
  "interests": ["culture", "food"],
  "travelers": "couple"
}
```
Response:
```json
{
  "id": "unique-plan-id",
  "itinerary": { }
}
```

### POST /api/payment/create-checkout
Request:
```json
{ "planId": "unique-plan-id" }
```
Response:
```json
{ "url": "https://checkout.stripe.com/..." }
```

### GET /api/payment/verify?session_id=...
Response:
```json
{ "paid": true, "planId": "..." }
```

---

## Claude API Configuration

### Model
```
claude-sonnet-4-20250514
```

### System Prompt
```
You are an expert travel planner with deep knowledge of destinations worldwide.
Create detailed, personalized, and practical travel itineraries.
Always use real, specific restaurant and attraction names.
Return ONLY valid JSON. No markdown, no explanation, no extra text.
```

### User Prompt Template
```
Create a {duration}-day travel itinerary for {destination}.
Travelers: {travelers}
Budget: {budget}
Interests: {interests}

Return ONLY this JSON structure:
{
  "tripTitle": "string",
  "destination": "string",
  "totalEstimatedCost": "string",
  "currency": "EUR",
  "days": [
    {
      "day": 1,
      "theme": "string",
      "morning": { "activity": "string", "location": "string", "duration": "string", "tip": "string" },
      "afternoon": { "activity": "string", "location": "string", "duration": "string", "tip": "string" },
      "evening": { "activity": "string", "location": "string", "duration": "string", "tip": "string" },
      "meals": {
        "breakfast": { "name": "string", "cuisine": "string", "priceRange": "string" },
        "lunch": { "name": "string", "cuisine": "string", "priceRange": "string" },
        "dinner": { "name": "string", "cuisine": "string", "priceRange": "string" }
      },
      "transport": "string",
      "dailyCost": "string",
      "insiderTip": "string"
    }
  ]
}
```

---

## TypeScript Interfaces (src/types/itinerary.ts)
```typescript
export interface Meal {
  name: string;
  cuisine: string;
  priceRange: string;
}

export interface DayPeriod {
  activity: string;
  location: string;
  duration: string;
  tip: string;
}

export interface ItineraryDay {
  day: number;
  theme: string;
  morning: DayPeriod;
  afternoon: DayPeriod;
  evening: DayPeriod;
  meals: {
    breakfast: Meal;
    lunch: Meal;
    dinner: Meal;
  };
  transport: string;
  dailyCost: string;
  insiderTip: string;
}

export interface Itinerary {
  tripTitle: string;
  destination: string;
  totalEstimatedCost: string;
  currency: string;
  days: ItineraryDay[];
}

export interface TripFormData {
  destination: string;
  duration: number;
  budget: 'budget' | 'mid-range' | 'luxury';
  interests: string[];
  travelers: 'solo' | 'couple' | 'family' | 'friends';
}
```

---

## Branding
- **Primary:** Forge Orange `#E85D04`
- **Secondary:** Dark Navy `#0D1B2A`
- **Accent:** Warm White `#FFF8F0`
- **Font:** Inter (Google Fonts)
- **Vibe:** Bold, adventurous, trustworthy

### Tailwind Custom Colors (tailwind.config.ts)
```ts
colors: {
  forge: {
    orange: '#E85D04',
    navy: '#0D1B2A',
    white: '#FFF8F0',
  }
}
```

---

## Hostinger Deployment

### Frontend (Static)
```bash
npm run build
# Upload /dist folder to Hostinger public_html via File Manager or FTP
```

### Backend (Node.js)
- Use Hostinger's Node.js hosting or a cheap VPS
- Entry point: `server/index.ts` (compiled to `server/dist/index.js`)
- Set environment variables in Hostinger panel
- Run: `node server/dist/index.js`

### Build Commands
```bash
# Frontend
npm run build

# Backend
cd server && npx tsc && node dist/index.js
```

---

## Code Style Rules
- Use functional components only — no class components
- Always type props with TypeScript interfaces
- Keep components small — max ~100 lines per file
- API calls only from `src/lib/api.ts` — never fetch directly in components
- Never put API keys in frontend code
- Use `async/await` — no `.then()` chains
- Handle loading and error states in every component that fetches data

---

## Common Commands
```bash
# Install dependencies
npm install

# Start frontend dev server (runs on http://localhost:3002)
npm run dev

# Start backend dev server (runs on http://localhost:3001)
cd server && npm run dev

# Build frontend for production
npm run build

# Type check
npx tsc --noEmit

# Run tests
npm test

# Run single test
npm test -- ComponentName
```

---

## Node.js Version
- Requires Node.js 18 or higher
- Recommended: Node.js 20 LTS
