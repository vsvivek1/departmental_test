import { newState, review, GRADES, assignTiers, planSession, streakInfo } from './scheduler.js';
const $ = document.getElementById('app');
const load = (k, d) => { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } };
const save = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} };
const data = await (await fetch('data.json')).json();
let exam = load('exam', ''), minutes = load('minutes', 7);
let states = load('states', {}), log = load('log', {}), queue = [], idx = 0, shown = false, secs = 0, doneToday = false;
const today = () => new Date().toISOString().slice(0, 10);
const cards = () => assignTiers(data.cards.filter(c => !exam || c.exams.includes(exam)));
const esc = s => String(s).replace(/[&<>]/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[m]));

function home() {
  const { streak, doneToday: d } = streakInfo(log), cs = cards();
  const plan = planSession({ cards: cs, states, minutes });
  $.innerHTML = `<h1>Departmental Test Prep</h1>
  <div class="card"><label class="mut">Exam</label><br><select id="ex"><option value="">All exams (mixed)</option>${data.exams.map(e => `<option ${e === exam ? 'selected' : ''}>${esc(e)}</option>`).join('')}</select>
  <p class="mut">${cs.length} questions ranked by how often they repeat in past papers. Open: tier ${plan.tier} of 3.</p></div>
  <div class="card"><b>${d ? 'Today is done. Streak: ' + streak + ' days' : 'Streak: ' + streak + ' days. Do at least ' + minutes + ' minutes today.'}</b>
  <p class="mut">${plan.dueCount} due now. Session fits about ${plan.cards.length} cards.</p>
  <button class="p" id="go">Start session</button></div>
  <p class="mut">Answers marked "pending" have no rule-book answer yet.</p>`;
  document.getElementById('ex').onchange = e => { exam = e.target.value; save('exam', exam); home(); };
  document.getElementById('go').onclick = () => start(plan);
  remind();
}
function start(plan) { queue = plan.cards.slice(); idx = 0; shown = false; secs = 0; doneToday = false; step(); }
function step() {
  if (idx >= queue.length) return finish();
  const c = queue[idx];
  $.innerHTML = `<p class="mut">Card ${idx + 1} of ${queue.length} · tier ${c.tier} · asked in ${c.sessions.length} session(s)</p>
  <div class="card q">${esc(c.question)}</div>
  ${shown ? answer(c) + `<div class="row"><button data-g="0">Forgot</button><button data-g="1">Hard</button><button data-g="2">Good</button><button data-g="3">Easy</button></div>` : `<button class="p" id="show" style="width:100%">Show answer</button>`}`;
  if (!shown) document.getElementById('show').onclick = () => { shown = true; step(); };
  $.querySelectorAll('[data-g]').forEach(b => b.onclick = () => grade(+b.dataset.g));
}
function answer(c) {
  if (!c.answer) return `<div class="card mut">Answer pending (rule-book answer not added yet). Recall it, then rate yourself.</div>`;
  return `<div class="card">${esc(c.answer)}${(c.quotes || []).map(q => `<div class="quote">“${esc(q.text)}”<div class="mut">${esc(q.ref)}</div></div>`).join('')}</div>`;
}
function grade(g) {
  const c = queue[idx]; states[c.id] = review(states[c.id] || newState(), g);
  if (g === 0) queue.push(c); // wrong cards come back in this session
  secs += 20; idx++; shown = false; save('states', states); step();
}
function finish() {
  log[today()] = 1; save('log', log);
  $.innerHTML = `<h1>Done for today</h1><p>Minimum reached. Want a few more?</p><div class="row"><button id="more" class="p">Keep going</button><button id="stop">Stop</button></div>`;
  document.getElementById('more').onclick = () => { const p = planSession({ cards: cards(), states, minutes: 5 }); p.cards.length ? start(p) : home(); };
  document.getElementById('stop').onclick = home;
}
function remind() { // at most one reminder per day, only if not studied yet today
  if (log[today()] || load('reminded') === today() || !('Notification' in window)) return;
  if (Notification.permission === 'default') Notification.requestPermission();
  if (Notification.permission === 'granted' && new Date().getHours() >= 18) { new Notification('Study 5 minutes today', { body: 'Your daily session is waiting.' }); save('reminded', today()); }
}
home();
