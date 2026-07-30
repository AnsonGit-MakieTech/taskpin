
# Office Plant — Feature Design (RPG Style)

## 1. Overview

**Office Plant** is a cozy RPG-style companion on **My Board**. Completing real tasks **feeds** the plant; streaks and level unlock **evolutions**. It uses existing TaskPin stats (completions, streak, level, XP) but does **not** replace the scoreboard — it’s a visual reward layer.

**One-line pitch:** *Your desk pet grows as you finish work.*

**Visual direction:** Warm cozy RPG (think Stardew Valley UI panels + TaskPin sticky-note palette) — **not** dark esports or hardcore MMO. Soft borders, stat cards, gentle glow, pixel-art or flat illustrated sprites.

**Core loop:**

```text
Complete task → Feed plant (+1) → Mood improves → Streak/Level → Evolution → New species + RPG title
Miss a day     → Mood drops (cosmetic only) → Plant recovers on next completion
```

**Rules (non-negotiable):**
- No XP loss for wilting
- No pay-to-win; plant never affects task permissions
- Wilting is gentle and reversible
- Plant is optional delight, not required to use TaskPin

---

## 2. RPG Presentation

### 2.1 Plant stat card (My Board widget)

RPG-style panel mounted above or beside the task list:

| Stat | Source | RPG label |
|---|---|---|
| Species | Evolution stage | **Class** |
| Stage | 0–5 | **Tier** |
| Mood | Last fed + streak | **Condition** |
| Total feeds | Lifetime completions counted | **Meals served** |
| Streak | `completion_streak` | **Daily buff** |
| User level | Scoreboard level | **Guardian rank** |

**UI chrome:**
- Ornate but soft frame (gold trim on cream, not black steel)
- Horizontal **Vitality bar** (mood, not HP loss from damage)
- Small buff icons when streak active (🔥 +1 day, +3, +7)
- Flavor text line that changes by mood (e.g. *“Ready for today’s quests!”*)

### 2.2 Mood system (Condition)

| Mood | Trigger | Visual | Flavor text |
|---|---|---|---|
| **Thriving** | Fed today + streak ≥ 3 | Glow, sparkles | *“On fire! Team MVP energy.”* |
| **Happy** | Fed today | Bright colors | *“Well fed and ready.”* |
| **Okay** | Fed yesterday | Normal | *“Could use a task snack.”* |
| **Sleepy** | 1 idle day | Droopy leaves | *“Zzz… pin something done?”* |
| **Wilting** | 2 idle days | Dull palette | *“Needs water (a completed task).”* |
| **Dormant** | 3+ idle days | Minimal animation | *“Waiting for you to return.”* |

Recovery: **one completed task** moves mood up one step (cap at Happy; Thriving still needs streak).

### 2.3 Evolution system (Class tiers)

Evolution uses **Guardian rank (level)** + **minimum total feeds**:

| Tier | Name | Unlock | Species (RPG class) |
|---|---|---|---|
| 0 | **Seed** | New user | Pin Seed in cracked pot |
| 1 | **Sprout** | Level 1, 1 feed | Desk Cactus |
| 2 | **Adventurer** | Level 5, 25 feeds | Quest Fern |
| 3 | **Hero** | Level 10, 75 feeds | Bonsai of Boards |
| 4 | **Champion** | Level 15, 150 feeds | Bloom Guardian |
| 5 | **Legend** | Level 20, 300 feeds | Golden Pin Tree |

Each tier has **5 mood sprites** + **1 evolution reveal sprite** + optional **idle animation frames**.

### 2.4 Feed moment (combat victory feel)

When user marks a task **Done** on My Board:
1. Short **+1 Feed** float text
2. Plant **bounce / chew** animation (4–8 frames)
3. Vitality bar tick up
4. If evolution threshold crossed → **Evolution modal** (RPG level-up screen)

Priority bonus (optional V1.5): Important feed = slightly bigger particle burst; Urgent = golden sparkles (no extra evolution speed required for MVP).

### 2.5 Streak buffs (RPG passive skills)

| Streak | Buff name | Effect (cosmetic) |
|---|---|---|
| 3 days | **Warm Desk** | Soft orange glow on pot |
| 7 days | **Fire Lamp** | Small flame/lamp prop appears on desk |
| 14 days | **Hero Aura** | Looping sparkle aura |
| 30 days | **Legendary Pot** | Pot skin upgrade (golden rim) |

Buffs are **visual only**; lost when streak breaks (except Legendary Pot — keep as earned trophy skin).

---

## 3. Screens & placement

| Screen | Content |
|---|---|
| **My Board** | Main plant widget + stat card (MVP) |
| **Scoreboard** | Tiny plant icon + mood dot on user row (V1.5) |
| **Evolution modal** | Full-screen or card overlay on tier-up |
| **Plant Codex** (V2) | Gallery of unlocked species + locked silhouettes |
| **Team Board** (V2) | Optional micro-plant on member tile |

MVP = **My Board only** + evolution modal.

---

## 4. Data (implementation hint)

Suggested fields on `UserProfile` or `OfficePlant` model:

```text
species_tier          (0–5)
mood                  (thriving|happy|okay|sleepy|wilting|dormant)
total_feeds           (int)
last_fed_date         (date)
streak_buff_tier      (0–4)
legendary_pot_owned   (bool)
evolution_seen_at     (timestamp, for one-time modal)
```

Feed hook: `mark_done` view after successful completion.

---

## 5. Full asset list

Convention: `static/assets/plant/` — PNG/WebP with transparency; optional `@2x` for retina.

**Recommended style:** 128×128 base sprite for plant; 512×320 for desk scene; UI panels as SVG where possible.

### 5.1 Desk / scene backgrounds (RPG environment)

| ID | Filename | Description | Size |
|---|---|---|---|
| BG-01 | `desk-tier-0-seedling.png` | Bare desk, single seed pot, corkboard blur | 512×320 |
| BG-02 | `desk-tier-1-sprout.png` | Small desk + sticky notes stack | 512×320 |
| BG-03 | `desk-tier-2-adventurer.png` | Wider desk, calendar, coffee mug | 512×320 |
| BG-04 | `desk-tier-3-hero.png` | Full corkboard wall behind desk | 512×320 |
| BG-05 | `desk-tier-4-champion.png` | Trophy shelf, warm lamp light | 512×320 |
| BG-06 | `desk-tier-5-legend.png` | Golden hour legendary office shrine | 512×320 |

### 5.2 Plant species — Tier 0: Pin Seed

| ID | Filename | Description |
|---|---|---|
| P0-HAPPY | `seed-happy.png` | Seed in soil, tiny sprout |
| P0-OKAY | `seed-okay.png` | Same, slightly muted |
| P0-SLEEPY | `seed-sleepy.png` | Drooped |
| P0-WILT | `seed-wilting.png` | Dry cracked soil |
| P0-DORMANT | `seed-dormant.png` | Greyscale seed only |
| P0-THRIVE | `seed-thriving.png` | Glow + micro sprout sparkle |

### 5.3 Plant species — Tier 1: Desk Cactus

| ID | Filename | Description |
|---|---|---|
| P1-HAPPY … P1-THRIVE | `cactus-{mood}.png` | 6 moods (same naming) |
| P1-IDLE | `cactus-idle-sheet.png` | Sprite sheet 4 frames blink/sway |
| P1-FEED | `cactus-feed-sheet.png` | 6 frames chew/bounce |
| P1-EVO | `cactus-evolution-reveal.png` | Hero pose for evolution modal |

### 5.4 Plant species — Tier 2: Quest Fern

| ID | Filename | Description |
|---|---|---|
| P2-HAPPY … P2-THRIVE | `fern-{mood}.png` | 6 moods |
| P2-IDLE | `fern-idle-sheet.png` | 4 frames |
| P2-FEED | `fern-feed-sheet.png` | 6 frames |
| P2-EVO | `fern-evolution-reveal.png` | Unfurling frond hero |

### 5.5 Plant species — Tier 3: Bonsai of Boards

| ID | Filename | Description |
|---|---|---|
| P3-HAPPY … P3-THRIVE | `bonsai-{mood}.png` | 6 moods |
| P3-IDLE | `bonsai-idle-sheet.png` | 4 frames |
| P3-FEED | `bonsai-feed-sheet.png` | 6 frames |
| P3-EVO | `bonsai-evolution-reveal.png` | Mini corkboard in branches |

### 5.6 Plant species — Tier 4: Bloom Guardian

| ID | Filename | Description |
|---|---|---|
| P4-HAPPY … P4-THRIVE | `bloom-{mood}.png` | 6 moods |
| P4-IDLE | `bloom-idle-sheet.png` | 4 frames |
| P4-FEED | `bloom-feed-sheet.png` | 6 frames |
| P4-EVO | `bloom-evolution-reveal.png` | Flower burst hero |

### 5.7 Plant species — Tier 5: Golden Pin Tree

| ID | Filename | Description |
|---|---|---|
| P5-HAPPY … P5-THRIVE | `goldtree-{mood}.png` | 6 moods |
| P5-IDLE | `goldtree-idle-sheet.png` | 4 frames shimmer |
| P5-FEED | `goldtree-feed-sheet.png` | 6 frames golden leaves |
| P5-EVO | `goldtree-evolution-reveal.png` | Legendary crown tree |

**Plant sprite subtotal:** 6 tiers × (6 moods + idle sheet + feed sheet + evo) ≈ **54 plant files** (+ sheets count as 1 each)

### 5.8 Pots & containers

| ID | Filename | Description |
|---|---|---|
| POT-01 | `pot-clay-default.png` | Starter pot |
| POT-02 | `pot-stripe-office.png` | Level 5 unlock |
| POT-03 | `pot-blue-quest.png` | Level 10 unlock |
| POT-04 | `pot-gold-champion.png` | Level 15 unlock |
| POT-05 | `pot-legendary-pin.png` | 30-day streak reward |
| POT-SHADOW | `pot-shadow.png` | Shared drop shadow under plant |

### 5.9 Streak buff props (desk overlays)

| ID | Filename | Description |
|---|---|---|
| PROP-01 | `buff-lamp-fire-7d.png` | 7-day streak lamp |
| PROP-02 | `buff-aura-hero-14d.png` | 14-day sparkle overlay (PNG sequence or CSS) |
| PROP-03 | `buff-desk-glow-3d.png` | Warm vignette overlay |

### 5.10 Feed & evolution VFX

| ID | Filename | Description |
|---|---|---|
| VFX-01 | `feed-sparkle-sheet.png` | 8 frames, white/yellow |
| VFX-02 | `feed-sparkle-important-sheet.png` | Orange burst |
| VFX-03 | `feed-sparkle-urgent-sheet.png` | Red/gold burst |
| VFX-04 | `float-plus-one-feed.png` | “+1 Feed” RPG damage-style float |
| VFX-05 | `evolution-rays.png` | Radial light behind evolution modal |
| VFX-06 | `evolution-stars-sheet.png` | 6 frames loop |
| VFX-07 | `level-up-banner.png` | “Evolution!” ribbon |
| VFX-08 | `confetti-sheet.png` | 8 frames (reuse from milestone if any) |

### 5.11 RPG UI chrome

| ID | Filename | Description |
|---|---|---|
| UI-01 | `panel-stat-card-bg.svg` | Main plant stat panel (9-slice or SVG) |
| UI-02 | `panel-stat-card-corner.svg` | Ornate corners overlay |
| UI-03 | `bar-vitality-track.svg` | Vitality bar background |
| UI-04 | `bar-vitality-fill.svg` | Fill (or CSS gradient) |
| UI-05 | `badge-mood-thriving.png` | 32×32 mood icons × 6 |
| UI-06 | `badge-mood-happy.png` | … |
| UI-07 | `badge-mood-okay.png` | … |
| UI-08 | `badge-mood-sleepy.png` | … |
| UI-09 | `badge-mood-wilting.png` | … |
| UI-10 | `badge-mood-dormant.png` | … |
| UI-11 | `icon-class-tier.png` | Generic tier star (32×32) |
| UI-12 | `icon-feed.png` | Feed action icon |
| UI-13 | `icon-streak-buff.png` | Flame buff icon |
| UI-14 | `modal-evolution-frame.svg` | Evolution popup frame |
| UI-15 | `btn-codex.svg` | “Plant Codex” button (V2) |

### 5.12 Codex / collection (V2)

| ID | Filename | Description |
|---|---|---|
| CODEX-01 | `codex-slot-empty.png` | Locked silhouette frame |
| CODEX-02 | `codex-slot-unlocked.png` | Filled frame |
| CODEX-03–08 | `codex-thumb-tier{0-5}.png` | Thumbnail per species |

### 5.13 Audio (optional but full RPG feel)

| ID | Filename | Description |
|---|---|---|
| SFX-01 | `feed-soft.mp3` | Short blip on feed |
| SFX-02 | `evolution-fanfare.mp3` | 2–3 sec cozy fanfare |
| SFX-03 | `mood-recover.mp3` | Gentle chime |
| SFX-04 | `ui-panel-open.mp3` | Stat card expand |

### 5.14 Marketing / empty states

| ID | Filename | Description |
|---|---|---|
| MKT-01 | `plant-empty-state-hero.png` | “Meet your office plant” onboarding |
| MKT-02 | `plant-onboarding-step1.png` | Complete tasks → feed |
| MKT-03 | `plant-onboarding-step2.png` | Streak → buffs |
| MKT-04 | `plant-onboarding-step3.png` | Level → evolution |

---

## 6. Asset summary count

| Category | Count (approx.) |
|---|---|
| Desk backgrounds | 6 |
| Plant moods (6 tiers × 6 moods) | 36 |
| Plant idle sheets | 6 |
| Plant feed sheets | 6 |
| Plant evolution reveals | 6 |
| Pots | 6 |
| Streak props | 3 |
| VFX | 8 |
| UI chrome | 15 |
| Codex (V2) | 8 |
| Audio (optional) | 4 |
| Onboarding | 4 |
| **Total (full build incl. V2 + audio)** | **~98 assets** |
| **MVP (Tier 0–1, 3 moods, 1 bg, core UI)** | **~25 assets** |

---

## 7. Build phases

### Phase 1 — MVP (fastest)
- 1 desk background (`desk-tier-1-sprout.png`)
- Tier 0–1 plants: happy / sleepy / wilting only (18 sprites → can cut to 9)
- Clay pot + stat panel SVG
- Feed float + simple bounce (CSS or 1 sheet)
- My Board widget only

### Phase 2 — Full moods + evolution
- All 6 moods, tiers 0–3, evolution modal, VFX sheets

### Phase 3 — Legend tier + codex + scoreboard icon
- Tiers 4–5, streak props, codex gallery, SFX

---

## 8. Art style guide (for artist / AI gen)

```text
Style:       Cozy RPG / office fantasy — soft pixel or flat illustration
Palette:     TaskPin warm (#FFF9C4, #FFE0B2, #FFCDD2, #FFB74D, #F8F6F0)
Outline:     Subtle 2px dark brown (#4A4540) optional
Lighting:    Warm top-left, soft shadows
Avoid:       Dark MMO UI, realistic 3D, horror wilt, gambling aesthetics
Reference:   Stardew stat panel + TaskPin sticky notes + rank badge tier colors
Export:      PNG-24 transparent; sheets horizontal; name files exactly as above
```

---

## 9. Tie-in to existing TaskPin systems

| TaskPin system | Office Plant use |
|---|---|
| `mark_done` | Trigger feed + animation |
| `completion_streak` | Mood Thriving + streak props |
| `level_from_xp()` | Evolution tier gates |
| `xp_for_completed_task()` | Optional VFX intensity by priority |
| Scoreboard rank badge | Same tier language (“Guardian rank”) |
| WebSocket `task.updated` | Live feed on My Board without refresh |

---

## 10. What we deliberately skip (V1)

- Spending XP in a plant shop (Phase 4 / Desk Builder merge)
- PvP or wagering
- Punitive XP loss
- Plant death / permanent failure
- Complex mini-game combat
 