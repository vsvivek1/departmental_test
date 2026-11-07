// Spaced-repetition session planner. Pure functions, no DOM. Works in browser and Node.
const DAY = 86400000, MIN = 60000;
export const GRADES = { forgot: 0, hard: 1, good: 2, easy: 3 };

export function newState() { return { ease: 2.3, interval: 0, due: 0, reps: 0, lapses: 0 }; }

// Estimated seconds a card takes: reading length plus extra for cards the user finds hard.
export function estSeconds(card, st) {
  const words = card.question.split(/\s+/).length;
  const hardness = 1 + Math.min(1, (st?.lapses || 0) * 0.25) + (card.answer ? 0 : 0);
  return Math.round((12 + words * 0.9) * hardness);
}

// Hard right-answers return sooner; easy ones go far; wrong ones come back in 10 minutes.
export function review(st, grade, now = Date.now()) {
  const s = { ...st, reps: st.reps + 1 };
  if (grade === GRADES.forgot) {
    s.lapses++; s.interval = 0; s.ease = Math.max(1.3, s.ease - 0.2); s.due = now + 10 * MIN; s.reps = 0;
    return s;
  }
  if (grade === GRADES.hard) { s.ease = Math.max(1.3, s.ease - 0.1); s.interval = Math.max(1, Math.round((s.interval || 1) * 1.2)); }
  else if (grade === GRADES.good) { s.interval = s.interval < 1 ? 1 : Math.round(s.interval * s.ease); }
  else { s.ease += 0.1; s.interval = s.interval < 1 ? 3 : Math.round(s.interval * s.ease * 1.3); }
  s.due = now + s.interval * DAY;
  return s;
}

// Tiers by exam frequency (not difficulty): tier 1 = most-repeated questions.
export function assignTiers(cards, sizes = [0.4, 0.35, 0.25]) {
  const sorted = [...cards].sort((a, b) => b.freq - a.freq || b.sessions.length - a.sessions.length);
  const n = sorted.length, cut1 = Math.ceil(n * sizes[0]), cut2 = cut1 + Math.ceil(n * sizes[1]);
  sorted.forEach((c, i) => { c.tier = i < cut1 ? 1 : i < cut2 ? 2 : 3; c.rank = i; });
  return sorted;
}

// Next tier opens once >= threshold of the previous tier has been reviewed at least once.
export function unlockedTier(cards, states, threshold = 0.7) {
  let tier = 1;
  while (tier < 3) {
    const t = cards.filter(c => c.tier === tier);
    const done = t.filter(c => (states[c.id]?.interval || 0) >= 1 || (states[c.id]?.reps || 0) >= 1).length;
    if (t.length && done / t.length >= threshold) tier++; else break;
  }
  return tier;
}

// Pull prerequisites (card.requires = [ids]) ahead of the card that needs them.
function withDeps(list, byId, states, seen = new Set()) {
  const out = [];
  const add = c => {
    if (!c || seen.has(c.id)) return;
    seen.add(c.id);
    (c.requires || []).forEach(id => { if (!states[id]?.reps) add(byId[id]); });
    out.push(c);
  };
  list.forEach(add);
  return out;
}

// Build one session: due/carry-over first (overdue spread via cap), then new cards by frequency,
// filled until the time budget runs out. extraMinutes lets the "keep going?" prompt extend it.
export function planSession({ cards, states, now = Date.now(), minutes = 7, overdueCap = 25, exclude = new Set() }) {
  const byId = Object.fromEntries(cards.map(c => [c.id, c]));
  const budget = minutes * 60;
  const due = cards.filter(c => states[c.id] && states[c.id].reps >= 0 && states[c.id].due && states[c.id].due <= now && !exclude.has(c.id))
    .sort((a, b) => states[a.id].due - states[b.id].due);
  // Missed-day spreading: at most overdueCap overdue (>1 day late) cards per session; rest wait for later days.
  let lateTaken = 0;
  const dueList = due.filter(c => {
    if (now - states[c.id].due > DAY) { if (lateTaken >= overdueCap) return false; lateTaken++; }
    return true;
  });
  const tier = unlockedTier(cards, states);
  const fresh = cards.filter(c => !states[c.id] && c.tier <= tier && !exclude.has(c.id)).sort((a, b) => a.tier - b.tier || a.rank - b.rank);
  // Interleave papers: round-robin by first paper within the frequency order, preserving rank within a paper.
  const pool = withDeps(fresh, byId, states);
  const plan = []; let spent = 0;
  for (const c of [...dueList, ...pool]) {
    const sec = estSeconds(c, states[c.id]);
    if (spent + sec > budget && plan.length) break;
    plan.push(c); spent += sec;
  }
  return { cards: plan, seconds: spent, dueCount: dueList.length, tier };
}

export function streakInfo(log, today = new Date()) {
  const key = d => d.toISOString().slice(0, 10);
  let streak = 0, d = new Date(today);
  if (!log[key(d)]) d = new Date(d - DAY);
  while (log[key(d)]) { streak++; d = new Date(d - DAY); }
  return { streak, doneToday: !!log[key(today)] };
}
