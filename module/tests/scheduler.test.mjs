import assert from 'node:assert/strict';
import { newState, review, GRADES, assignTiers, unlockedTier, planSession, streakInfo } from '../web/scheduler.js';
const now = 1_700_000_000_000, DAY = 86400000;
const mk = (n) => Array.from({ length: n }, (_, i) => ({ id: 'c' + i, question: 'word '.repeat(10), freq: n - i, sessions: ['a'] }));

let s = review(newState(), GRADES.forgot, now);
assert.equal(s.due, now + 600000, 'forgot returns in 10 minutes');
const good = review(review(newState(), GRADES.good, now), GRADES.good, now);
const hard = review(review(newState(), GRADES.good, now), GRADES.hard, now);
assert.ok(hard.interval < good.interval, 'hard gap shorter than good gap');

const cards = mk(10); assignTiers(cards);
assert.equal(cards[0].tier, 1); assert.equal(cards[9].tier, 3);
assert.equal(unlockedTier(cards, {}), 1);
const t1 = cards.filter(c => c.tier === 1), st = {};
t1.forEach(c => st[c.id] = review(newState(), GRADES.good, now));
assert.equal(unlockedTier(cards, st), 2, 'tier 2 opens after tier 1 mostly done');

// due first, new next, budget respected
const states = { c5: { ...newState(), reps: 1, due: now - 1000 } };
const p = planSession({ cards, states, now, minutes: 2 });
assert.equal(p.cards[0].id, 'c5', 'due before new');
assert.ok(p.seconds <= 120 + 40);
// missed-day spreading
const old = {}; mk(40).forEach(c => old[c.id] = { ...newState(), reps: 1, due: now - 3 * DAY });
const big = mk(40); assignTiers(big);
assert.equal(planSession({ cards: big, states: old, now, minutes: 60, overdueCap: 10 }).dueCount, 10);
// streak
const d = new Date('2026-11-07T10:00:00Z');
assert.deepEqual(streakInfo({ '2026-11-07': 1, '2026-11-06': 1 }, d), { streak: 2, doneToday: true });
console.log('scheduler tests passed');
