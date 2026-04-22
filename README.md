# Tripforge

AI-powered travel planner web app.

**Tagline:** "Forge your perfect journey"

Users input destination, duration, budget, and interests — the app generates a detailed day-by-day itinerary using the Anthropic Claude API.

## Quick Start

### Frontend

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build
```

### Backend

```bash
cd server

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build
npm start
```

## Environment Setup

1. Copy `.env.example` to `.env` in both root and `server/` directories
2. Add your API keys:
   - Get an Anthropic API key from [console.anthropic.com](https://console.anthropic.com)
   - Get Stripe keys from [stripe.com](https://stripe.com)

## Project Structure

```
tripforge/
├── src/               # Frontend React app
├── server/            # Express backend
├── public/            # Static assets
├── CLAUDE.md          # Claude Code guidance
└── README.md          # This file
```

## Tech Stack

- **Frontend:** Vite + React 18 + TypeScript + Tailwind CSS
- **Backend:** Express.js + TypeScript
- **AI:** Anthropic Claude API
- **Payments:** Stripe
- **PDF:** jsPDF

## License

MIT
