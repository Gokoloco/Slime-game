# STUDIO NOTES: Slime (Game 2, working name)

Repo: Gokoloco/Slime-game. Last updated: 20 Nov 2026 (prototype v0.1, not published).

## What it is
Mobile-first slime-making mini-game. Two modes chosen at start:
- **Chill:** no timer, no score, free mixing, share image.
- **Challenge:** timed mixing round scored on finger moves, leaderboard, time-pressure effects.

Full design lives in the Game Studio HQ project: BRIEF_Slime, RESEARCH_Slime_Satisfaction, SLIME_Asset_Catalog.

## Rules (current)
- Moves: rotate right, rotate left, up-down. Repeating the same move slows mixing; switching moves speeds it up.
- Texture phases: 1 Gluey, 2 Stringy, 3 Smooth (ready reveal).
- Glitter unlock: extra points and about +3 s (to tune). Max total time capped.
- Effects are gentle, no rapid flashing, "reduce effects" toggle.

## Numbers (to tune in playtests)
- Round length: 45 s, max 60 s. Low-time effects start at 10 s. Idle pause after 6 s without touch.
- Glitter: every 5th different move in a row gives +50 points and +3 s. Finishing a slime: +100 and +3 s.
- Repeating a move: speed 1 - 0.25 per repeat (floor 0.25). Switching: speed 1 + 0.1 per switch (cap 1.5). Score multiplier 1 + 0.25 per switch (cap x3).
- Progress per move: 3.2 x speed. Phase 2 at 33, phase 3 at 66, ready at 100.

## Status (v0.1 prototype)
Done: slime body (soft-body, stable at 30 and 60 fps), 3 phases with different look, touch/stretch/snap, circle and up-down gestures, mix-speed meter, Chill (6 colors) and Challenge modes, glitter, tilt and buzz at low time, effects and sound toggles, synthesized sounds (original, no licence needed), idle pause.
Not done: leaderboard, nickname, share button, real art/stones/add-ins, unlock progression, long gluey strings when stretching, privacy page.

## Tests
`python3 tests/test_slime.py` (needs Playwright + Chrome). 20 headless checks: gestures with simulated pointer input, variety rule, phases, glitter, timer, tilt, idle pause, console errors.
NOT tested: real phone touch feel, gesture accuracy on real fingers, sound on real devices, iOS Safari, performance on low-end phones.

## Conventions
Single `docs/index.html`, assets in `docs/assets`, hosted free first (GitHub Pages). Own Supabase table for leaderboard, no accounts, filtered nicknames, no ads/analytics.

## To-do
- [ ] Prototype: slime body, phases, gestures, meter
- [ ] Chill and Challenge modes
- [ ] Sound (licence check)
- [ ] Art batch (Magnific, commercial-use terms check first)
- [ ] Leaderboard (Supabase, own table)
- [ ] Real-phone test, then publish after approval
- [ ] Name, trademark and privacy page (before launch)


## Colour mixing (v0.2, 20 Nov 2026)
- Every slime starts as plain milky base. Tapping a swatch ADDS a colour: it appears as swirling streaks and only blends in slowly while you mix (blend +0.07 x speed per move, about 14 good moves).
- Blend is paint-like (hue wheel): red + yellow = orange, blue + yellow = green. First colour on the milky base is strong (85%), later colours are half-half (50%).
- A half-mixed colour is folded in if you add another one before it finished.
- Challenge: each new slime starts with a random colour to mix in. When fully mixed a toast names the colour.
- Tests: 27 headless checks pass (7 new for colour). Not tested on a real phone yet.
- Idea: colour combos as collectibles (name list), Magnific art for textures and glitters.
