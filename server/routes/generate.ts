import { Router } from 'express';
import { generateItinerary } from '../lib/claude.js';
import { checkRateLimit } from '../lib/rateLimit.js';
import { randomUUID } from 'crypto';

const router = Router();

// In-memory store for generated plans (use a database in production)
const generatedPlans = new Map();

router.post('/', async (req, res) => {
  try {
    const { destination, duration, budget, interests, travelers } = req.body;

    // Validate required fields
    if (!destination || !duration || !budget || !travelers) {
      return res.status(400).json({
        error: 'Missing required fields'
      });
    }

    // Check rate limit
    const ip = req.ip || req.socket.remoteAddress || 'unknown';
    const rateLimit = checkRateLimit(ip);

    if (!rateLimit.allowed) {
      return res.status(429).json({
        error: 'Rate limit exceeded. Try again tomorrow.',
        remaining: 0
      });
    }

    // Generate itinerary using Claude
    const itinerary = await generateItinerary({
      destination,
      duration,
      budget,
      interests: interests || [],
      travelers
    });

    // Store the generated plan
    const planId = randomUUID();
    generatedPlans.set(planId, {
      itinerary,
      createdAt: new Date(),
      ip,
      paid: false
    });

    res.json({
      id: planId,
      itinerary,
      remaining: rateLimit.remaining
    });
  } catch (error) {
    console.error('Error generating itinerary:', error);
    res.status(500).json({
      error: 'Failed to generate itinerary'
    });
  }
});

// Get a generated plan by ID
router.get('/:id', (req, res) => {
  const { id } = req.params;
  const plan = generatedPlans.get(id);

  if (!plan) {
    return res.status(404).json({ error: 'Plan not found' });
  }

  res.json({
    id,
    itinerary: plan.itinerary,
    paid: plan.paid
  });
});

export default router;
