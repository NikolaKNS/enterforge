interface RateLimitEntry {
  count: number;
  resetTime: number;
}

// In-memory store for rate limiting (use Redis in production)
const rateLimitStore = new Map<string, RateLimitEntry>();

const RATE_LIMIT = 3; // requests per window
const WINDOW_MS = 24 * 60 * 60 * 1000; // 24 hours

export function checkRateLimit(ip: string): { allowed: boolean; remaining: number } {
  const now = Date.now();
  const entry = rateLimitStore.get(ip);

  if (!entry || now > entry.resetTime) {
    // New window
    rateLimitStore.set(ip, {
      count: 1,
      resetTime: now + WINDOW_MS
    });
    return { allowed: true, remaining: RATE_LIMIT - 1 };
  }

  if (entry.count >= RATE_LIMIT) {
    return { allowed: false, remaining: 0 };
  }

  entry.count++;
  return { allowed: true, remaining: RATE_LIMIT - entry.count };
}

export function getRateLimitResetTime(ip: string): number | null {
  const entry = rateLimitStore.get(ip);
  return entry?.resetTime || null;
}
