import express, { Router } from 'express';
import Stripe from 'stripe';
import dotenv from 'dotenv';

dotenv.config();

const router = Router();

// Initialize Stripe
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || '', {
  apiVersion: '2024-06-20'
});

// In-memory store (use a database in production)
const generatedPlans = new Map();

// Create checkout session
router.post('/create-checkout', async (req, res) => {
  try {
    const { planId } = req.body;

    if (!planId) {
      return res.status(400).json({ error: 'Plan ID is required' });
    }

    // Get plan details (from your database)
    // const plan = await getPlan(planId);

    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: [
        {
          price_data: {
            currency: 'eur',
            product_data: {
              name: 'Tripforge Full Itinerary',
              description: 'Complete travel plan with PDF export'
            },
            unit_amount: 499 // €4.99
          },
          quantity: 1
        }
      ],
      mode: 'payment',
      success_url: `${process.env.FRONTEND_URL}/result/${planId}?payment=success`,
      cancel_url: `${process.env.FRONTEND_URL}/result/${planId}`,
      metadata: {
        planId
      }
    });

    res.json({ url: session.url });
  } catch (error) {
    console.error('Error creating checkout session:', error);
    res.status(500).json({ error: 'Failed to create checkout session' });
  }
});

// Verify payment
router.get('/verify', async (req, res) => {
  try {
    const { session_id } = req.query;

    if (!session_id || typeof session_id !== 'string') {
      return res.status(400).json({ error: 'Session ID is required' });
    }

    const session = await stripe.checkout.sessions.retrieve(session_id);

    if (session.payment_status === 'paid') {
      // Mark the plan as paid
      const planId = session.metadata?.planId;
      if (planId) {
        // Update in your database
        // await markPlanAsPaid(planId);
      }

      res.json({
        paid: true,
        planId: session.metadata?.planId
      });
    } else {
      res.json({ paid: false });
    }
  } catch (error) {
    console.error('Error verifying payment:', error);
    res.status(500).json({ error: 'Failed to verify payment' });
  }
});

// Webhook for Stripe events
router.post('/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
  const sig = req.headers['stripe-signature'];

  if (!sig) {
    return res.status(400).send('Missing signature');
  }

  try {
    const event = stripe.webhooks.constructEvent(
      req.body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET || ''
    );

    if (event.type === 'checkout.session.completed') {
      const session = event.data.object as Stripe.Checkout.Session;
      const planId = session.metadata?.planId;

      if (planId) {
        // Mark plan as paid in your database
        console.log(`Payment completed for plan: ${planId}`);
      }
    }

    res.json({ received: true });
  } catch (error) {
    console.error('Webhook error:', error);
    res.status(400).send('Webhook error');
  }
});

export default router;
