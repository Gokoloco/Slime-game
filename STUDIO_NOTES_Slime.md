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

## Challenge colours and glitter (v0.3, 20 Nov 2026)
- Colour and glitter buttons now show in BOTH modes. Challenge no longer auto-adds a random colour: you choose.
- Challenge scoring: every move scores, a fully mixed colour = +40, 5 different moves in a row = 1 glitter charge.
- Glitter is a button you tap: Silver (1 charge), Gold (1 charge), Rainbow (2 charges, rare). Each charge used = +50 points, and a use gives +3 s (capped at 60 s). Chill: glitter free.
- Menu now explains both modes. 33 headless checks pass. Not tested on a real phone.

## Left-right swipe, marks, gluey stretch, new layout (v0.4, 20 Nov 2026)
- New move H (left-right): swipe one way and back, straight enough (same rule as up-down). Counts as a different move for variety/streaks. Ignored while a circle is being drawn.
- Slime marks: while the finger holds slime it leaves a pale smear that fades in about 2 s.
- Gluey stretch (phase 1 strongest, phase 2 thinner, none in phase 3): the lump is capped at 0.6R, the rest of the pull is a neck plus a blob on the finger. On snap the strand springs back.
- Layout: glitters in vertical columns left (Silver, Gold) and right (Rainbow), colours along the bottom.
- 39 headless checks pass. Not tested on a real phone. The strand and the swipe thresholds will need tuning after real play.

## Multi-finger stretch, breaking, rejoining (v0.5, 20 Nov 2026)
- Every finger that holds the slime pulls its own part (own gluey strand per finger). Pull in several directions at once.
- Stress: pulling a finger past 75% of the phase limit builds stress (about 1.25 s at the limit with one finger, faster with more fingers). A grip that tears off adds +0.3. Stress melts away at 0.7/s when you relax. Rim turns red, slime trembles, Stress bar shows, warning at 50%.
- At 100% stress the slime breaks into 5 pieces (they share the slime's area). Penalty: progress -30, variety streak and speed reset, no mixing while broken. Challenge also: -100 points and -5 s (BREAK_POINTS, BREAK_TIME).
- Rejoin: drag pieces with fingers; pieces pull gently towards each other and merge when they touch; one piece left = whole slime again (plop wobble). Time keeps running in Challenge, so the delay is the extra cost.
- Gestures (circles, swipes) only count with one finger on the screen.
- Tests: 50 headless checks (synthetic multi-pointer events). NOT tested with real multi-touch on a phone: that is the first thing to check (iOS Safari multi-touch, browser gestures, palm touches).
- To tune after play: stress speed (0.8/s), limits per phase, merge distance (0.8), piece attraction (0.06), penalties.

## Colour field: marbled, uneven, multi-colour mixing (v0.6, 21 Nov 2026)
- The slime now has a colour map (28 x 28 cells, 6 pigments + milky base). Tapping a colour drops a big patch plus a few drips at a random spot; the rest stays milky. Several colours can be added at once and mix at the same time.
- Moves stir it: circles swirl the colours (inner part turns faster = spirals), up-down and left-right moves fold them, every move spends "mixing work" that diffuses the colours. Better variety = faster. Repeating = slow (stiff slime barely mixes).
- Paint-like mixing: red + yellow = orange, blue + yellow = green (partly cancelling opposite hues, so it never turns plain grey). A later colour takes room from the milky base first and only pushes older colours aside by 40%.
- Done = unevenness (TV) below 0.045; Challenge pays +40 once per added colour. Label shows "color N% mixed". Pace about 12-18 good moves per colour.
- Numbers to tune: MIX_ITER 8, DIFFUSE 0.2, MEAN_PULL 0.003, TV_DONE 0.045, target colour amount 0.85 first / 0.4 later.
- 53 headless checks pass (run twice). Colours still look pastel on purpose; not tested on a real phone. Performance on slow phones is unchecked (field update every frame while mixing).

## v0.7 Magnific art (20 Nov 2026)
- Art in `docs/assets` (record of ids/prompts in `assets/ASSETS.md`): workshop background (CSS, with a dark scrim at the bottom for the meters), gluey slime texture (overlay inside the body, strongest in phase 1), glitter layers (silver/gold/rainbow, screen blend, slowly turning and twinkling), Glowstone pop-up.
- Slime home moved down to 0.56·H so it sits on the table.
- Perfect slime reward: slime finished + glitter added + a colour fully mixed in + never broken = Glowstone (+200 in Challenge, pop-up, counted on the end screen).
- Images preload; the game still works without them (falls back to the old look).
- Tested: 53/53 headless checks, screenshots of menu and play, Glowstone trigger (+310 = 10 move +100 ready +200 stone). NOT tested: real phones, load time on slow mobile data (assets ~0.6 MB), Safari blend modes.
- Open: Magnific commercial-use terms must be checked BEFORE public launch. Redo smooth texture without hands (xSBQJAwjfW). Toast text is hard to read over the busy background (add a pill). Glitter L/R column split unconfirmed.
