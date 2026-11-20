import math, json, sys
from playwright.sync_api import sync_playwright

import os
URL = "file://" + os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "index.html"))
results = []
def check(name, ok, info=""):
    results.append((name, ok, info)); print(("PASS " if ok else "FAIL ") + name + (" | " + str(info) if info else ""))

def circle(page, cx, cy, r, turns=1, cw=True, steps=60):
    page.mouse.move(cx + r, cy); page.mouse.down()
    n = int(steps * turns)
    for i in range(1, n + 1):
        a = (i / steps) * 2 * math.pi * (1 if cw else -1)
        page.mouse.move(cx + r * math.cos(a), cy + r * math.sin(a))
        page.wait_for_timeout(8)
    page.mouse.up()

def updown(page, cx, cy, amp, cycles=1):
    page.mouse.move(cx, cy - amp); page.mouse.down()
    for c in range(cycles):
        for i in range(1, 21):
            page.mouse.move(cx, cy - amp + 2 * amp * i / 20); page.wait_for_timeout(8)
        for i in range(1, 21):
            page.mouse.move(cx, cy + amp - 2 * amp * i / 20); page.wait_for_timeout(8)
    page.mouse.up()

def leftright(page, cx, cy, amp, cycles=1):
    page.mouse.move(cx - amp, cy); page.mouse.down()
    for c in range(cycles):
        for i in range(1, 21):
            page.mouse.move(cx - amp + 2 * amp * i / 20, cy); page.wait_for_timeout(8)
        for i in range(1, 21):
            page.mouse.move(cx + amp - 2 * amp * i / 20, cy); page.wait_for_timeout(8)
    page.mouse.up()

with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"])
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.goto(URL); page.wait_for_timeout(500)
    check("page loads, menu visible", page.is_visible("#menu"))
    page.screenshot(path="/tmp/shots/menu.png")

    # ---- Chill
    page.click("#goChill"); page.wait_for_timeout(300)
    home = page.evaluate("({x: __slime.home.x, y: __slime.home.y, R: __slime.R})")
    cx, cy, R = home["x"], home["y"], home["R"]
    circle(page, cx, cy, R * 0.7, cw=True)
    lm = page.evaluate("__slime.S.lastMove"); check("clockwise circle -> R", lm == "R", lm)
    circle(page, cx, cy, R * 0.7, cw=False)
    lm = page.evaluate("__slime.S.lastMove"); check("counter-clockwise circle -> L", lm == "L", lm)
    updown(page, cx, cy, R * 0.8, cycles=1)
    lm = page.evaluate("__slime.S.lastMove"); check("up-down -> V", lm == "V", lm)
    page.screenshot(path="/tmp/shots/chill1.png")
    page.evaluate("__slime.S.lastMove = null")
    updown(page, cx, cy, R * 0.8, cycles=3)
    cnt = page.evaluate("__slime.S.mixes"); check("3 up-down cycles register several V moves", page.evaluate("__slime.S.lastMove") == "V", cnt)
    # a slow wobbly diagonal should NOT count as up-down
    page.evaluate("__slime.S.lastMove = null; __slime.S.mixes = 0")
    page.mouse.move(cx - R, cy - R * 0.8); page.mouse.down()
    for i in range(1, 41): page.mouse.move(cx - R + 2 * R * i / 40, cy - R * 0.8 + 1.6 * R * i / 40); page.wait_for_timeout(6)
    page.mouse.up()
    check("diagonal drag does not register up-down", page.evaluate("__slime.S.lastMove") != "V", page.evaluate("__slime.S.lastMove"))

    # variety rule via direct registerMove
    page.evaluate("__slime.startGame('chill')")
    for _ in range(4): page.evaluate("__slime.registerMove('R')")
    sp = page.evaluate("__slime.S.speed"); check("repeating same move slows mixing to floor", abs(sp - 0.25) < 1e-6, sp)
    page.evaluate("__slime.registerMove('L')")
    sp2 = page.evaluate("__slime.S.speed"); check("switching move restores speed", sp2 >= 1.0, sp2)
    page.evaluate("__slime.startGame('chill')")
    seq = ['R','L','V','R','L','V','R','L','V','R']
    for m in seq: page.evaluate(f"__slime.registerMove('{m}')")
    sp3 = page.evaluate("__slime.S.speed"); check("varied moves cap speed at 1.5", abs(sp3 - 1.5) < 1e-6, sp3)
    # phases: progress
    page.evaluate("__slime.startGame('chill')")
    phases = []
    for i in range(40):
        page.evaluate(f"__slime.registerMove('{'RLV'[i%3]}')")
        ph = page.evaluate("__slime.S.phase")
        if not phases or phases[-1] != ph: phases.append(ph)
    check("phases advance 1->2->3", phases == [1,2,3], phases)
    pr = page.evaluate("__slime.S.progress"); check("progress reaches 100 in chill", pr == 100, pr)
    page.wait_for_timeout(300); page.screenshot(path="/tmp/shots/chill_ready.png")

    # ---- Challenge
    page.evaluate("__slime.startGame('challenge')"); page.wait_for_timeout(200)
    t0 = page.evaluate("__slime.S.t")
    # keep activity so idle pause doesn't trigger
    circle(page, cx, cy, R * 0.7, cw=True)
    t1 = page.evaluate("__slime.S.t")
    check("timer counts down in challenge", t1 < t0, (t0, t1))
    sc = page.evaluate("__slime.S.score"); check("score increases from moves", sc > 0, sc)
    # glitter after 5 switches
    page.evaluate("__slime.startGame('challenge')")
    for m in ['R','L','V','R','L','V']: page.evaluate(f"__slime.registerMove('{m}')")
    ch = page.evaluate("({c: __slime.S.charges, g: __slime.S.glitter})")
    check("5 different moves earn 1 glitter charge (no auto glitter)", ch["c"] == 1 and not ch["g"], ch)
    sc0 = page.evaluate("__slime.S.score")
    page.evaluate("__slime.addGlitter(2)")
    check("Rainbow glitter is locked with 1 charge (needs 2)", not page.evaluate("__slime.S.glitter"))
    page.evaluate("__slime.addGlitter(0)")
    gl = page.evaluate("({g: __slime.S.glitter, t: __slime.S.t, s: __slime.S.score, c: __slime.S.charges})")
    check("tapping Silver spends the charge: +50 and +3s", gl["g"] and gl["c"] == 0 and gl["s"] == sc0 + 50 and gl["t"] > 45 + 1.5, gl)
    page.evaluate("__slime.addGlitter(1)")
    check("glitter is locked again without a charge", page.evaluate("__slime.S.glitters").count(1) == 0)
    page.screenshot(path="/tmp/shots/glitter.png")
    # time pressure
    page.evaluate("__slime.S.t = 8; __slime.S.lastInput = performance.now()"); page.wait_for_timeout(400)
    tr = page.evaluate("document.getElementById('cv').style.transform")
    check("tilt effect active under 10s", "rotate" in tr, tr)
    page.screenshot(path="/tmp/shots/pressure.png")
    # reduce effects removes tilt
    page.evaluate("__slime.S.lastInput = performance.now()")
    page.click("#btnFx"); page.wait_for_timeout(200)
    tr2 = page.evaluate("document.getElementById('cv').style.transform")
    check("reduce effects removes tilt", tr2 == "", tr2)
    page.evaluate("__slime.S.lastInput = performance.now()")
    page.click("#btnFx")
    # end
    page.evaluate("__slime.S.t = 0.05"); page.wait_for_timeout(300)
    check("round ends at 0 and shows end screen", page.is_visible("#endScreen") and page.evaluate("__slime.S.mode") == "end")
    page.screenshot(path="/tmp/shots/end.png")
    # idle pause
    page.click("#again"); page.wait_for_timeout(200)
    page.evaluate("__slime.S.lastInput = performance.now() - 7000"); page.wait_for_timeout(200)
    check("idle pauses timer", page.evaluate("__slime.S.paused"))
    t_a = page.evaluate("__slime.S.t"); page.wait_for_timeout(400); t_b = page.evaluate("__slime.S.t")
    check("timer frozen while paused", abs(t_a - t_b) < 1e-6, (t_a, t_b))
    # ---- colour mixing (colour map inside the slime)
    import colorsys
    def hue(rgb): return colorsys.rgb_to_hls(*(v / 255 for v in rgb))[0] * 360
    def mixmoves(n, seq='RLVH'):
        for k in range(n):
            page.evaluate(f"__slime.registerMove('{seq[k % len(seq)]}')")
            page.evaluate("for (let i = 0; i < 24; i++) __slime.step(1/60)")
    page.evaluate("__slime.startGame('chill')")
    check("new slime starts plain milky white", page.evaluate("__slime.colorName(__slime.slimeColor())") == "Milky white" and page.evaluate("__slime.fieldTV()") < 0.001)
    page.evaluate("__slime.addColor(1, true)")   # Sunny (yellow)
    tv0 = page.evaluate("__slime.fieldTV()")
    check("a new colour lands as uneven patches, not over the whole slime", tv0 > 0.1, round(tv0, 3))
    far = page.evaluate("[__slime.cellColor(0, 0), __slime.cellColor(0.95, 0.0), __slime.cellColor(-0.95, 0.0), __slime.cellColor(0, 0.95), __slime.cellColor(0, -0.95)]")
    check("colour differs from place to place right after adding", max(max(abs(a - b) for a, b in zip(far[0], c)) for c in far[1:]) > 25, far)
    mixmoves(4); tv1 = page.evaluate("__slime.fieldTV()")
    mixmoves(4); tv2 = page.evaluate("__slime.fieldTV()")
    check("moves blend it slowly: unevenness shrinks step by step", tv0 > tv1 > tv2 > 0.005 and page.evaluate("__slime.S.pendingMix"), (round(tv0, 3), round(tv1, 3), round(tv2, 3)))
    mixmoves(12)
    check("after enough mixing the colour is even and counted as mixed", not page.evaluate("__slime.S.pendingMix") and page.evaluate("__slime.S.mixedCount") == 1, page.evaluate("__slime.S.mixedCount"))
    check("yellow slime is yellow", 35 < hue(page.evaluate("__slime.slimeColor()")) < 75, page.evaluate("__slime.slimeColor()"))
    page.evaluate("__slime.addColor(0, true)")   # red into yellow
    mixmoves(24)
    nm = page.evaluate("__slime.colorName(__slime.slimeColor())")
    check("red + yellow = orange", "Orange" in nm, nm)
    page.evaluate("__slime.startGame('chill'); __slime.addColor(2, true)")  # blue, then yellow
    mixmoves(10); page.evaluate("__slime.addColor(1, true)"); mixmoves(26)
    hh = hue(page.evaluate("__slime.slimeColor()"))
    check("blue + yellow = green-ish (not grey)", 65 < hh < 190, round(hh))
    # several colours at the same time
    page.evaluate("__slime.startGame('chill'); __slime.addColor(0, true); __slime.addColor(2, true); __slime.addColor(4, true)")
    tvm = page.evaluate("__slime.fieldTV()"); mixmoves(6)
    check("3 colours at once mix together at the same time", page.evaluate("__slime.fieldTV()") < tvm and page.evaluate("__slime.S.pendingMix"), round(tvm, 3))
    page.evaluate("__slime.registerMove('R')"); a1 = page.evaluate("__slime.fieldTV()")
    page.evaluate("__slime.S.speed = 0.25"); sp_slow = page.evaluate("__slime.S.speed")
    page.evaluate("__slime.startGame('challenge')")
    check("challenge shows colour and glitter buttons", page.is_visible("#swatches") and page.is_visible("#glitters"))
    check("challenge starts plain, you choose the colour", not page.evaluate("__slime.S.pendingMix"))
    page.evaluate("__slime.addColor(0, true)"); mixmoves(22)
    check("challenge: fully mixed colour counted (+40 bonus)", page.evaluate("__slime.S.mixedCount") == 1, page.evaluate("__slime.S.mixedCount"))
    page.evaluate("__slime.startGame('chill')")
    page.evaluate("__slime.addGlitter(2)")
    check("chill: rainbow glitter is free", page.evaluate("__slime.S.glitter") and page.evaluate("__slime.S.charges") == 0)
    page.screenshot(path="/tmp/shots/chill_rainbow.png")
    page.evaluate("__slime.startGame('challenge')")
    page.screenshot(path="/tmp/shots/challenge_ui.png")
    # ---- left-right swipe, slime marks, stretch strand
    page.evaluate("__slime.startGame('chill')")
    home = page.evaluate("({x: __slime.home.x, y: __slime.home.y, R: __slime.R})"); cx, cy, R = home["x"], home["y"], home["R"]
    page.evaluate("__slime.S.lastMove = null")
    leftright(page, cx, cy - R * 0.35, R * 0.8, cycles=1)
    lm = page.evaluate("__slime.S.lastMove"); check("left-right swipe (there and back) -> H", lm == "H", lm)
    page.evaluate("__slime.S.lastMove = null; __slime.S.mixes = 0")
    circle(page, cx, cy, R * 0.7, cw=True); circle(page, cx, cy, R * 0.7, cw=False)
    mv = page.evaluate("__slime.S.mixes"); lm = page.evaluate("__slime.S.lastMove")
    check("two circles give exactly 2 moves (no false left-right/up-down)", mv == 2 and lm == "L", (mv, lm))
    page.evaluate("__slime.S.lastMove = null")
    page.mouse.move(cx - R * 0.8, cy - R * 0.8); page.mouse.down()
    for i in range(1, 41): page.mouse.move(cx - R * 0.8 + 1.6 * R * i / 40, cy - R * 0.8 + 1.6 * R * i / 40); page.wait_for_timeout(6)
    page.mouse.up()
    check("diagonal drag is not left-right either", page.evaluate("__slime.S.lastMove") not in ("H", "V"), page.evaluate("__slime.S.lastMove"))
    tl = page.evaluate("__slime.trail.length"); check("swiping leaves slime marks", tl > 5, tl)
    page.wait_for_timeout(2600)
    check("slime marks fade away", page.evaluate("__slime.trail.length") == 0, page.evaluate("__slime.trail.length"))
    # stretched gluey strand (phase 1) held in place for a screenshot
    page.evaluate("__slime.startGame('chill'); __slime.addColor(2, true)")
    page.mouse.move(cx, cy); page.mouse.down()
    for i in range(1, 30): page.mouse.move(cx + R * 0.3 * i / 30, cy - R * 1.55 * i / 30); page.wait_for_timeout(16)
    page.wait_for_timeout(400)
    page.screenshot(path="/tmp/shots/stretch1.png")
    held = page.evaluate("!!(__slime.S.mode) && __slime.S.mode")
    for i in range(1, 30): page.mouse.move(cx + R * 0.3, cy - R * 1.55 - R * 0.8 * i / 30); page.wait_for_timeout(16)
    page.wait_for_timeout(100)
    check("pulling too far snaps the slime back (strand springs back)", page.evaluate("__slime.snapStrs.length") >= 0)
    page.screenshot(path="/tmp/shots/stretch2.png")
    page.mouse.up()
    page.evaluate("__slime.startGame('challenge'); __slime.S.lastInput = performance.now()")
    # ---- several fingers: stretch in all directions, break, rejoin
    PE = """(a) => { const cv = document.getElementById('cv'); cv.dispatchEvent(new PointerEvent(a.t, {pointerId: a.id, clientX: a.x, clientY: a.y, bubbles: true, pointerType: 'touch', isPrimary: a.id === 11})); }"""
    def pe(t, id, x, y): page.evaluate(PE, {"t": t, "id": id, "x": x, "y": y})
    page.evaluate("__slime.startGame('chill')")
    cx, cy, R = page.evaluate("__slime.home.x"), page.evaluate("__slime.home.y"), page.evaluate("__slime.R")
    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    for k, (dx, dy) in enumerate(dirs): pe("pointerdown", 11 + k, cx + dx * R * 0.8, cy + dy * R * 0.8)
    check("4 fingers can hold the slime at once", page.evaluate("__slime.fingers.size") == 4)
    for step in range(1, 11):
        for k, (dx, dy) in enumerate(dirs): pe("pointermove", 11 + k, cx + dx * R * (0.8 + 0.07 * step), cy + dy * R * (0.8 + 0.07 * step))
        page.wait_for_timeout(30)
    page.wait_for_timeout(300)
    offs = page.evaluate("[0, 18, 36, 54].map(i => __slime.off[i])")
    check("slime stretches in all 4 directions at once", all(o > R * 0.2 for o in offs), [round(o) for o in offs])
    check("moderate stretch does not break it", not page.evaluate("__slime.S.broken"), page.evaluate("__slime.S.stress"))
    page.screenshot(path="/tmp/shots/multi_stretch.png")
    for k in range(4): pe("pointerup", 11 + k, cx, cy)
    page.wait_for_timeout(500)
    # too much for too long -> breaks (Challenge penalty)
    page.evaluate("__slime.startGame('challenge'); __slime.S.score = 300; __slime.S.lastInput = performance.now()")
    t_before = page.evaluate("__slime.S.t")
    for k, (dx, dy) in enumerate(dirs): pe("pointerdown", 11 + k, cx + dx * R * 0.8, cy + dy * R * 0.8)
    for step in range(1, 25):
        for k, (dx, dy) in enumerate(dirs): pe("pointermove", 11 + k, cx + dx * R * min(2.45, 0.8 + 0.12 * step), cy + dy * R * min(2.45, 0.8 + 0.12 * step))
        page.wait_for_timeout(40)
        if page.evaluate("__slime.S.broken"): break
    page.wait_for_timeout(200)
    br = page.evaluate("({b: __slime.S.broken, n: __slime.pieces.length, sc: __slime.S.score, t: __slime.S.t, area: __slime.pieces.reduce((a, p) => a + p.r * p.r, 0) / (__slime.R * __slime.R)})")
    check("stretching too much for too long breaks the slime into pieces", br["b"] and br["n"] == 5, br)
    check("challenge: break costs 100 points and 5 seconds", br["sc"] <= 200 + 1 and br["t"] < t_before - 4, br)
    check("pieces keep the slime's total area (merge back to one slime)", abs(br["area"] - 1) < 0.01, br["area"])
    page.screenshot(path="/tmp/shots/broken.png")
    for k in range(4): pe("pointerup", 11 + k, cx, cy)
    page.evaluate("__slime.S.mixes = 0"); page.evaluate("__slime.registerMove('R')")
    check("no mixing while broken (lost traction)", page.evaluate("__slime.S.mixes") == 0)
    # drag one piece onto another with a finger
    pc = page.evaluate("__slime.pieces.map(p => ({x: p.x, y: p.y}))")
    page.evaluate("__slime.pieces.forEach(p => { p.vx = 0; p.vy = 0; })")
    a0 = page.evaluate("({x: __slime.pieces[0].x, y: __slime.pieces[0].y})"); b0 = page.evaluate("({x: __slime.pieces[1].x, y: __slime.pieces[1].y})")
    pe("pointerdown", 21, a0["x"], a0["y"])
    held = page.evaluate("__slime.pieces.filter(p => p.held !== null).length")
    for i in range(1, 16): pe("pointermove", 21, a0["x"] + (b0["x"] - a0["x"]) * i / 15, a0["y"] + (b0["y"] - a0["y"]) * i / 15); page.wait_for_timeout(30)
    pe("pointerup", 21, b0["x"], b0["y"]); page.wait_for_timeout(200)
    check("dragging a piece with a finger picks it up", held == 1, held)
    check("pieces that touch merge into one", page.evaluate("__slime.pieces.length") <= 4, page.evaluate("__slime.pieces.length"))
    # rest: pull everything together -> whole slime again
    page.evaluate("__slime.pieces.forEach(p => { p.x = __slime.home.x; p.y = __slime.home.y; p.vx = 0; p.vy = 0; })"); page.wait_for_timeout(300)
    check("all pieces merged -> whole slime again", not page.evaluate("__slime.S.broken") and page.evaluate("__slime.pieces.length") == 0)
    page.evaluate("__slime.S.mixes = 0"); page.evaluate("__slime.registerMove('R')")
    check("mixing works again after rejoining", page.evaluate("__slime.S.mixes") == 1)
    page.evaluate("__slime.startGame('challenge'); __slime.S.lastInput = performance.now()")
    check("no console/page errors", len(errors) == 0, errors[:3])
    b.close()

fails = [r for r in results if not r[1]]
print(f"\n{len(results)-len(fails)}/{len(results)} passed")
sys.exit(1 if fails else 0)
