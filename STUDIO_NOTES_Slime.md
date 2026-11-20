# STUDIO NOTES: Slime (Game 2, working name)

Repo: Gokoloco/Slime-game. Last updated: 20 Nov 2026.

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
- Round length: TBD
- Time bonus per glitter: +3 s
- Slowdown per repeated move: TBD

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
