# TaskPin Office Plant RPG

## Complete Asset Generation Order and Prompts

## Important generation workflow

Do not generate all assets independently. That will cause inconsistent plants, pots, proportions, lighting, and outlines.

Follow this process:

1. Generate the visual style sheet.
2. Approve the style.
3. Generate the base desk scene.
4. Generate each plant’s **Happy** version first.
5. Use the approved Happy plant as the image reference for its other moods.
6. Use the same approved plant reference for idle, feeding, and evolution assets.
7. Keep the same camera angle, canvas size, pot position, lighting, and outline thickness.

For every follow-up asset, attach the previously approved reference and include:

```text
Use the attached approved TaskPin Office Plant artwork as the exact visual reference. Preserve the same character design, proportions, pot position, camera angle, outline thickness, lighting, and color palette.
```

---

# Master visual-style prompt

Use this prompt before the asset-specific instruction:

```text
Create one production-ready visual asset for the TaskPin Office Plant RPG feature.

Art direction: cozy office fantasy RPG, clean flat 2D illustration with subtle game-inspired details, friendly and professional, warm TaskPin sticky-note palette, cream backgrounds, soft yellow, warm orange, muted green, calm blue, and dark brown outlines.

Use subtle 2px dark-brown outlines, warm top-left lighting, soft shadows, simple readable shapes, clean edges, and restrained decorative details.

The result must feel like part of a friendly productivity application, not a dark fantasy game, esports interface, casino game, realistic 3D render, or children’s cartoon.

Do not include unrelated objects, logos, watermarks, mockup devices, browser frames, or additional text unless explicitly requested.

Generate only the requested asset.
```

---

# Step 0 — Visual style anchor

This is a reference sheet and does not become part of the application.

## 0. `office-plant-style-reference.png`

```text
Create a visual style reference sheet for TaskPin Office Plant RPG.

Show six coordinated examples in one clean presentation:
1. Pin Seed
2. Desk Cactus
3. Quest Fern
4. Bonsai of Boards
5. Bloom Guardian
6. Golden Pin Tree

Also show one clay pot, one warm office desk background sample, one cream-and-gold RPG panel, one vitality bar, and three simple mood icons.

Use a consistent cozy office RPG illustration style, warm TaskPin colors, subtle dark-brown outlines, soft top-left lighting, and friendly readable silhouettes.

This is an art-direction sheet only. Keep all examples visually consistent and clearly separated.
```

Approve this reference before creating production assets.

---

# Phase 1 — Core MVP assets

## 1. `desk-tier-1-sprout.png`

**Size:** 512×320
**Background:** Full scene

```text
Create a cozy illustrated office desk scene for the Tier 1 Desk Cactus stage.

Show a warm wooden desktop, softly blurred corkboard wall, a small stack of yellow sticky notes, one pencil cup, and a subtle window-light glow from the upper left.

Leave a clear central area for a plant and pot to be layered on top. Do not include the actual plant.

Use a warm cream, yellow, orange, muted green, and brown palette. Keep the environment simple, uncluttered, friendly, and suitable for a productivity application.

Canvas size 512×320, full rectangular background, no text.
```

---

## 2. `panel-stat-card-bg.svg`

Generate as a large transparent PNG reference, then recreate or trace it as SVG.

```text
Create a scalable RPG-style stat panel background for the TaskPin Office Plant widget.

Use a warm cream panel, soft beige inner surface, subtle golden-brown border, gently rounded corners, and very restrained ornamental details inspired by office stationery and sticky-note corners.

Leave the center empty for HTML text and statistics. Do not include labels, icons, buttons, or text.

Front-facing flat UI asset, transparent outside the panel, no perspective, no mockup.
```

---

## 3. `panel-stat-card-corner.svg`

```text
Create one decorative corner ornament for the TaskPin Office Plant stat panel.

Use a soft golden-brown line design combining a small leaf, pushpin, and subtle stationery flourish. Keep it minimal and professional.

The ornament must work when mirrored into all four corners. Transparent background, no panel body, no text.
```

---

## 4. `bar-vitality-track.svg`

```text
Create an empty vitality-bar track for a cozy office RPG interface.

Use a cream and light-brown rounded frame with a shallow inset appearance, soft inner shadow, and subtle gold edge.

The center must remain empty for a separate fill layer. Horizontal orientation, transparent background, no text or icons.
```

---

## 5. `bar-vitality-fill.svg`

```text
Create the fill layer for the Office Plant vitality bar.

Use a soft green-to-yellow horizontal progression with a gentle highlight and rounded ends. Keep the style warm, calm, and suitable for a productivity application.

Generate only the fill shape on a transparent background. No frame, text, icon, or percentage.
```

---

## 6. `modal-evolution-frame.svg`

```text
Create a centered evolution-modal frame for TaskPin Office Plant RPG.

Use a warm cream panel with a slightly more prestigious gold-brown border than the normal stat panel. Add restrained leaf, star, sticky-note, and pushpin ornaments around the edges.

Leave a large empty center for the evolved plant illustration, title, statistics, and button. Transparent outside the panel, front-facing, no text.
```

---

# Mood icons

Generate every mood icon with the same circular frame and illustration style.

## 7. `badge-mood-happy.png`

```text
Create a 64×64 circular mood badge representing Happy.

Show a bright green leaf with a small cheerful expression, warm yellow highlight, cream circular background, and soft brown outline.

Transparent outside the badge. No text.
```

## 8. `badge-mood-thriving.png`

```text
Create a 64×64 circular mood badge representing Thriving.

Show a glowing green leaf with three small golden sparkles and an energetic cheerful expression. Use the same frame and proportions as the approved Happy mood badge.

Transparent outside the badge. No text.
```

## 9. `badge-mood-okay.png`

```text
Create a 64×64 circular mood badge representing Okay.

Show a calm green leaf with a neutral relaxed expression. Use slightly muted colors while preserving the same frame and proportions as the Happy badge.

Transparent outside the badge. No text.
```

## 10. `badge-mood-sleepy.png`

```text
Create a 64×64 circular mood badge representing Sleepy.

Show a slightly drooping green leaf with closed eyes and one very small sleep symbol. Preserve the same frame and proportions as the Happy badge.

Transparent outside the badge. No text.
```

## 11. `badge-mood-wilting.png`

```text
Create a 64×64 circular mood badge representing Wilting.

Show a gently drooping muted-green leaf with a concerned but non-distressing expression. The plant must appear recoverable, not dead.

Preserve the same frame and proportions as the Happy badge. Transparent outside the badge. No text.
```

## 12. `badge-mood-dormant.png`

```text
Create a 64×64 circular mood badge representing Dormant.

Show a sleeping folded leaf in muted sage and beige colors with a calm resting expression. It must feel peaceful rather than damaged.

Preserve the same frame and proportions as the Happy badge. Transparent outside the badge. No text.
```

---

# Core stat icons

## 13. `icon-class-tier.png`

```text
Create a 64×64 RPG stat icon representing plant class and evolution tier.

Combine a small golden star with a green leaf inside a friendly cream-and-brown emblem.

Transparent background, centered, no text.
```

## 14. `icon-feed.png`

```text
Create a 64×64 RPG stat icon representing feeding through completed tasks.

Show a small yellow sticky note with a green check mark being offered to a happy leaf.

Transparent background, centered, no text.
```

## 15. `icon-streak-buff.png`

```text
Create a 64×64 RPG stat icon representing a completion streak buff.

Show a small warm-orange flame combined with a green leaf and tiny golden sparkle.

Friendly productivity-game style, transparent background, centered, no text.
```

---

# Starter pot assets

## 16. `pot-clay-default.png`

**Size:** 128×128 transparent canvas

```text
Create the default Office Plant clay pot.

Show a small friendly terracotta office plant pot in a three-quarter front view. Use warm orange-brown clay, a soft rim highlight, subtle surface texture, and clean dark-brown outline.

The pot must sit centered near the bottom of a 128×128 transparent canvas. Do not include a plant, soil animation, face, text, or shadow.
```

## 17. `pot-shadow.png`

```text
Create a soft oval grounding shadow for the Office Plant pots.

Use a subtle warm gray-brown transparent shadow, horizontally stretched and softly blurred.

Generate only the shadow on a transparent 128×128 canvas. No pot or plant.
```

---

# Tier 0 — Pin Seed

Use the approved `seed-happy.png` as the reference for all other Seed assets.

## 18. `seed-happy.png`

```text
Create the Tier 0 Pin Seed character for TaskPin Office Plant RPG.

Show a tiny green sprout emerging from dark soil inside the approved clay pot. Include two small leaves, a friendly cheerful expression, and one tiny yellow pushpin-shaped marker beside the sprout.

Three-quarter front view, centered on a 128×128 transparent canvas. Keep the silhouette simple and readable. No extra objects or text.
```

## 19. `seed-okay.png`

```text
Edit the approved Pin Seed character into the Okay mood.

Keep the exact plant, pot, proportions, soil, pushpin marker, lighting, and camera angle. Give the sprout a calm neutral expression and slightly reduce the color saturation.

Transparent 128×128 canvas. Do not redesign the character.
```

## 20. `seed-sleepy.png`

```text
Edit the approved Pin Seed character into the Sleepy mood.

Keep the exact design and pot. Slightly lower the leaves, close the eyes, and add a gentle sleepy posture. Do not make the plant unhealthy.

Transparent 128×128 canvas.
```

## 21. `seed-wilting.png`

```text
Edit the approved Pin Seed character into the Wilting mood.

Keep the same character and pot. Gently droop the leaves, slightly mute the green color, and show lightly dry soil. The plant must look recoverable and non-distressing.

Transparent 128×128 canvas.
```

## 22. `seed-dormant.png`

```text
Edit the approved Pin Seed character into the Dormant mood.

Keep the same pot, soil position, and character proportions. Show the sprout folded low and peacefully resting, using muted sage colors and closed eyes.

Do not show plant death or severe damage. Transparent 128×128 canvas.
```

## 23. `seed-thriving.png`

```text
Edit the approved Pin Seed character into the Thriving mood.

Keep the exact character and pot. Make the leaves slightly brighter and more upright, add a warm glow, and include three small golden sparkles.

Transparent 128×128 canvas.
```

## 24. `seed-idle-sheet.png`

**Size:** 512×128

```text
Create a horizontal four-frame idle animation sprite sheet for the approved Pin Seed.

Frame sequence:
1. Neutral happy pose
2. Slight upward sway
3. Tiny blink
4. Return sway

Keep the pot completely stationary and keep the plant centered on the same baseline in every frame.

Four equal 128×128 frames, transparent background, no labels, borders, or frame numbers.
```

## 25. `seed-feed-sheet.png`

**Size:** 768×128

```text
Create a horizontal six-frame feeding animation sprite sheet for the approved Pin Seed.

Show a tiny sticky-note task snack appearing, the sprout leaning toward it, a cheerful bite or absorption moment, one small bounce, and a return to the happy pose.

Keep the pot stationary and preserve the exact character design.

Six equal 128×128 frames, transparent background, no labels or borders.
```

## 26. `seed-evolution-reveal.png`

```text
Create a polished evolution-reveal illustration of the approved Pin Seed transforming toward Desk Cactus.

Show the Seed standing proudly in its clay pot with warm golden light, rising green energy, small sticky-note particles, and a hopeful heroic pose.

Centered on a 512×512 transparent canvas. No text, frame, banner, or background scene.
```

---

# Tier 1 — Desk Cactus

## 27. `cactus-happy.png`

```text
Create the Tier 1 Desk Cactus character.

Show a small rounded cactus with two friendly arms inside the approved clay pot. Give it a cheerful face, three small cactus spikes represented safely and softly, and one tiny yellow sticky note pinned near the pot rim.

Three-quarter front view, centered on a 128×128 transparent canvas. Friendly, simple, and readable.
```

## 28. `cactus-okay.png`

```text
Edit the approved Desk Cactus into the Okay mood.

Keep the exact cactus anatomy, arms, pot, pinned note, lighting, and camera angle. Use a neutral expression and slightly calmer colors.

Transparent 128×128 canvas.
```

## 29. `cactus-sleepy.png`

```text
Edit the approved Desk Cactus into the Sleepy mood.

Keep the exact design. Lower the cactus arms slightly, close the eyes, and create a gentle sleepy lean.

Transparent 128×128 canvas.
```

## 30. `cactus-wilting.png`

```text
Edit the approved Desk Cactus into the Wilting mood.

Keep the exact design and pot. Slightly lower the arms, mute the green color, and add a mildly tired expression. It must look recoverable, not damaged.

Transparent 128×128 canvas.
```

## 31. `cactus-dormant.png`

```text
Edit the approved Desk Cactus into the Dormant mood.

Keep the exact character proportions and pot. Show closed eyes, relaxed lowered arms, and muted sage coloring. The character should look peacefully inactive.

Transparent 128×128 canvas.
```

## 32. `cactus-thriving.png`

```text
Edit the approved Desk Cactus into the Thriving mood.

Keep the exact design and pot. Raise its arms slightly, brighten the green color, add a warm aura, and include small golden sparkles.

Transparent 128×128 canvas.
```

## 33. `cactus-idle-sheet.png`

```text
Create a horizontal four-frame idle animation sprite sheet for the approved Desk Cactus.

Sequence: normal pose, slight left sway, blink, slight right sway. Keep the pot stationary and preserve the same baseline.

Four equal 128×128 frames on a transparent 512×128 canvas. No labels or borders.
```

## 34. `cactus-feed-sheet.png`

```text
Create a horizontal six-frame feeding animation sprite sheet for the approved Desk Cactus.

Show a sticky-note snack appearing, the cactus noticing it, leaning forward, absorbing or chewing it, making one cheerful bounce, and returning to its happy pose.

Keep the pot stationary.

Six equal 128×128 frames on a transparent 768×128 canvas. No labels or borders.
```

## 35. `cactus-evolution-reveal.png`

```text
Create a polished hero illustration of the approved Desk Cactus for its evolution reveal.

Show the cactus proudly raising both arms with warm golden rays, small sticky-note particles, subtle green energy, and a cheerful victorious expression.

Centered on a 512×512 transparent canvas. No text, banner, modal frame, or background.
```

---

# Core feed and evolution effects

## 36. `feed-sparkle-sheet.png`

```text
Create a horizontal eight-frame particle animation for a normal Office Plant feeding event.

Use small soft-yellow stars, white sparkles, tiny green leaves, and subtle glowing dots. The particles should expand outward and fade gently.

Transparent background, eight equal frames, no plant, text, or interface.
```

## 37. `float-plus-one-feed.png`

```text
Create a compact RPG-style floating reward graphic reading “+1 Feed”.

Use friendly rounded lettering, warm yellow fill, dark-brown outline, and one small green leaf accent. Keep the text highly readable at small size.

Transparent background, no panel or additional words.
```

## 38. `evolution-rays.png`

```text
Create soft radial evolution rays for the Office Plant evolution modal.

Use warm cream, pale yellow, and subtle gold beams radiating from the center. Keep the effect gentle and cozy rather than explosive.

Transparent background, no plant, text, stars, or frame.
```

## 39. `evolution-stars-sheet.png`

```text
Create a horizontal six-frame looping evolution-star animation.

Use small golden stars, cream sparkles, and soft glowing points rotating gently around an empty center area.

Transparent background, six equal frames, no plant, text, or frame.
```

## 40. `level-up-banner.png`

```text
Create a cozy RPG ribbon banner displaying the word “EVOLUTION!”

Use warm golden-yellow fabric, cream highlights, dark-brown outline, small leaf ornaments, and subtle pushpin details.

Transparent background, centered, highly readable, no other words.
```

## 41. `confetti-sheet.png`

```text
Create a horizontal eight-frame celebration-confetti animation.

Use small sticky-note squares, green leaves, yellow stars, and orange paper strips. Keep the effect warm and restrained.

Transparent background, eight equal frames, no plant, text, or UI.
```

---

# Introductory empty state

## 42. `plant-empty-state-hero.png`

```text
Create a welcoming onboarding illustration for “Meet your Office Plant”.

Show the happy Desk Cactus sitting on a cozy office desk beside several completed sticky notes, a small corkboard, warm sunlight, and subtle sparkles.

Leave clear empty space on the right side for interface text. Friendly productivity-app artwork, 512×320, no embedded words.
```

---

# Phase 2 — Remaining desk environments

## 43. `desk-tier-0-seedling.png`

```text
Create the Tier 0 Office Plant desk background.

Show a very simple warm wooden desk, softly blurred empty corkboard, one small pencil, and a modest beginner workspace. Leave a clear central position for the Seed and pot.

Do not include the plant or pot. Full 512×320 background, no text.
```

## 44. `desk-tier-2-adventurer.png`

```text
Create the Tier 2 Quest Fern desk background.

Show a wider organized office desk with a small calendar, coffee mug, folded task list, pencil cup, and a few pinned sticky notes on a corkboard.

Leave a clear central area for the plant. Warm cozy lighting, 512×320, no plant or text.
```

## 45. `desk-tier-3-hero.png`

```text
Create the Tier 3 Bonsai of Boards desk background.

Show a full corkboard wall with neatly organized sticky notes, a polished wooden desk, task folders, and a small desk clock. The environment should feel more accomplished but remain uncluttered.

Leave the plant area empty. Full 512×320 background, no text.
```

## 46. `desk-tier-4-champion.png`

```text
Create the Tier 4 Bloom Guardian desk background.

Show a warm office desk with a trophy shelf, glowing desk lamp, framed achievement badge, and organized sticky-note board.

Use richer gold, green, and warm-orange accents while preserving the cozy TaskPin style. Leave the plant area empty. 512×320, no text.
```

## 47. `desk-tier-5-legend.png`

```text
Create the Tier 5 Golden Pin Tree desk background.

Show a legendary but tasteful office shrine at golden hour: premium wooden desk, softly glowing corkboard, golden pin ornaments, completed-task scrolls, and subtle achievement trophies.

Keep it professional and calm, not royal or extravagant. Leave the plant area empty. Full 512×320 background, no text.
```

---

# Tier 2 — Quest Fern

## 48. `fern-happy.png`

```text
Create the Tier 2 Quest Fern character.

Show a friendly green fern with several curved fronds inside the approved office-striped pot. Add a tiny adventurer satchel tag and one small quest-marker pin.

Give it a cheerful expression within the central leaves. Three-quarter front view, 128×128 transparent canvas.
```

## 49. `fern-okay.png`

```text
Edit the approved Quest Fern into the Okay mood.

Preserve the exact fronds, accessories, pot, proportions, and camera angle. Relax the expression and slightly mute the colors.

Transparent 128×128 canvas.
```

## 50. `fern-sleepy.png`

```text
Edit the approved Quest Fern into the Sleepy mood.

Keep the exact design. Gently lower several fronds, close the eyes, and create a calm resting posture.

Transparent 128×128 canvas.
```

## 51. `fern-wilting.png`

```text
Edit the approved Quest Fern into the Wilting mood.

Preserve the design and accessories. Gently droop the outer fronds, mute the greens, and use a tired but recoverable expression.

Transparent 128×128 canvas.
```

## 52. `fern-dormant.png`

```text
Edit the approved Quest Fern into the Dormant mood.

Keep the same design and pot. Fold the fronds inward slightly, close the eyes, and use peaceful muted colors.

Do not make the fern appear dead. Transparent 128×128 canvas.
```

## 53. `fern-thriving.png`

```text
Edit the approved Quest Fern into the Thriving mood.

Keep the exact design. Raise and spread the fronds, brighten the green colors, add a warm glow, and include golden quest sparkles.

Transparent 128×128 canvas.
```

## 54. `fern-idle-sheet.png`

```text
Create a horizontal four-frame idle sprite sheet for the approved Quest Fern.

Show a gentle frond sway, a blink, and a return to the base pose. Keep the pot stationary and all frames aligned.

Four equal 128×128 frames, transparent 512×128 canvas.
```

## 55. `fern-feed-sheet.png`

```text
Create a horizontal six-frame feeding sprite sheet for the approved Quest Fern.

Show a sticky-note snack appearing, the fronds reaching toward it, the task note being absorbed, a cheerful unfurling bounce, and a return to Happy.

Six equal 128×128 frames, transparent 768×128 canvas.
```

## 56. `fern-evolution-reveal.png`

```text
Create a hero evolution illustration for the approved Quest Fern.

Show the fern dramatically unfurling its fronds with warm green energy, golden quest sparkles, and floating sticky-note particles.

Centered on a transparent 512×512 canvas. No text or frame.
```

---

# Tier 3 — Bonsai of Boards

## 57. `bonsai-happy.png`

```text
Create the Tier 3 Bonsai of Boards character.

Show a compact friendly bonsai tree with a curved trunk, rounded green foliage clusters, and three miniature sticky notes pinned among its branches. Place it in the approved blue quest pot.

Give it a calm confident expression. Three-quarter front view, transparent 128×128 canvas.
```

## 58. `bonsai-okay.png`

```text
Edit the approved Bonsai of Boards into the Okay mood.

Preserve the exact trunk, foliage, pinned notes, pot, lighting, and proportions. Use a neutral expression and slightly calmer colors.

Transparent 128×128 canvas.
```

## 59. `bonsai-sleepy.png`

```text
Edit the approved Bonsai of Boards into the Sleepy mood.

Keep the exact design. Lower the outer foliage slightly, close the eyes, and create a gentle resting posture.

Transparent 128×128 canvas.
```

## 60. `bonsai-wilting.png`

```text
Edit the approved Bonsai of Boards into the Wilting mood.

Preserve the trunk, sticky notes, and pot. Slightly droop the foliage clusters and mute the greens. Keep the plant clearly recoverable.

Transparent 128×128 canvas.
```

## 61. `bonsai-dormant.png`

```text
Edit the approved Bonsai of Boards into the Dormant mood.

Keep the same tree and pot. Show peacefully closed eyes, subdued foliage, and a quiet resting pose.

Do not show dead branches or fallen leaves. Transparent 128×128 canvas.
```

## 62. `bonsai-thriving.png`

```text
Edit the approved Bonsai of Boards into the Thriving mood.

Preserve the exact design. Make the foliage fuller and brighter, add warm green-and-gold glow, and illuminate the miniature sticky notes.

Transparent 128×128 canvas.
```

## 63. `bonsai-idle-sheet.png`

```text
Create a horizontal four-frame idle sprite sheet for the approved Bonsai of Boards.

Show a subtle leaf sway, a blink, one tiny sticky-note flutter, and return to the base pose. Keep the pot and trunk baseline stationary.

Four equal 128×128 frames, transparent 512×128 canvas.
```

## 64. `bonsai-feed-sheet.png`

```text
Create a horizontal six-frame feeding sprite sheet for the approved Bonsai of Boards.

Show a completed sticky note floating toward the branches, being pinned into the foliage, a gentle tree bounce, a brief sparkle, and a return to Happy.

Six equal 128×128 frames, transparent 768×128 canvas.
```

## 65. `bonsai-evolution-reveal.png`

```text
Create a hero evolution illustration for the approved Bonsai of Boards.

Show the bonsai with expanded glowing branches, miniature corkboard elements among the foliage, warm golden rays, and floating completed sticky notes.

Centered on a transparent 512×512 canvas. No text or frame.
```

---

# Streak-buff overlays

## 66. `buff-desk-glow-3d.png`

```text
Create a subtle three-day streak desk-glow overlay.

Use a warm orange-and-gold vignette concentrated around the plant area, with very soft light and no visible object.

Transparent 512×320 overlay, no desk, plant, text, or frame.
```

## 67. `buff-lamp-fire-7d.png`

```text
Create a small cozy seven-day streak desk lamp.

Show a compact office lamp with a warm flame-shaped light inside, muted orange metal, cream highlight, and subtle golden glow.

Transparent background, designed to sit on the right side of the desk scene. No text.
```

## 68. `buff-aura-hero-14d.png`

```text
Create a fourteen-day streak hero-aura overlay.

Show a gentle circular aura of small golden sparkles, green leaf particles, and soft light around an empty center where the plant will appear.

Transparent background, no plant, text, or frame.
```

---

# Priority feeding effects

## 69. `feed-sparkle-important-sheet.png`

```text
Create a horizontal eight-frame feeding-particle animation for an Important task.

Use warm orange stars, yellow sticky-note fragments, subtle green leaves, and a slightly larger burst than the standard feed effect.

Transparent background, eight equal frames, no text or plant.
```

## 70. `feed-sparkle-urgent-sheet.png`

```text
Create a horizontal eight-frame feeding-particle animation for an Urgent task.

Use controlled red, warm gold, orange sparkles, and tiny sticky-note fragments. Make it prestigious but not alarming, explosive, or casino-like.

Transparent background, eight equal frames, no text or plant.
```

---

# Unlockable pots

## 71. `pot-stripe-office.png`

```text
Create the Level 5 Office Stripe pot.

Use the exact dimensions and three-quarter camera angle of the approved clay pot. Add clean cream-and-orange horizontal office stripes and a slightly polished finish.

Transparent 128×128 canvas, no plant or shadow.
```

## 72. `pot-blue-quest.png`

```text
Create the Level 10 Blue Quest pot.

Use the exact dimensions and angle of the approved clay pot. Use calm blue ceramic, a cream rim, and one small golden quest-star emblem.

Transparent 128×128 canvas, no plant or shadow.
```

## 73. `pot-gold-champion.png`

```text
Create the Level 15 Gold Champion pot.

Use the exact dimensions and angle of the approved clay pot. Use warm muted gold, a dark-brown base, subtle leaf engravings, and restrained premium highlights.

Avoid excessive shine. Transparent 128×128 canvas, no plant or shadow.
```

## 74. `pot-legendary-pin.png`

```text
Create the permanent 30-day streak Legendary Pin pot.

Use the exact dimensions and camera angle of the approved pot. Use cream ceramic with a golden rim, one elegant pushpin crest, subtle green accents, and a soft prestige glow.

Premium but professional. Transparent 128×128 canvas, no plant or shadow.
```

---

# Tier 4 — Bloom Guardian

## 75. `bloom-happy.png`

```text
Create the Tier 4 Bloom Guardian character.

Show a strong but friendly flowering plant with layered green leaves and one large warm-orange central bloom. Shape the surrounding leaves subtly like a protective shield.

Place it in the approved Gold Champion pot. Give it a calm confident expression. Transparent 128×128 canvas.
```

## 76. `bloom-okay.png`

```text
Edit the approved Bloom Guardian into the Okay mood.

Preserve the exact bloom, leaves, shield silhouette, pot, proportions, and lighting. Relax the expression and slightly reduce saturation.

Transparent 128×128 canvas.
```

## 77. `bloom-sleepy.png`

```text
Edit the approved Bloom Guardian into the Sleepy mood.

Keep the exact design. Lower the outer leaves slightly, partially close the central bloom, and show peacefully closed eyes.

Transparent 128×128 canvas.
```

## 78. `bloom-wilting.png`

```text
Edit the approved Bloom Guardian into the Wilting mood.

Preserve the design and pot. Gently lower the leaves and flower, mute the colors, and use a tired but recoverable expression.

Transparent 128×128 canvas.
```

## 79. `bloom-dormant.png`

```text
Edit the approved Bloom Guardian into the Dormant mood.

Keep the same design. Fold the bloom and leaves inward slightly, close the eyes, and use peaceful muted colors.

Do not show dead petals. Transparent 128×128 canvas.
```

## 80. `bloom-thriving.png`

```text
Edit the approved Bloom Guardian into the Thriving mood.

Preserve the exact design. Fully open the central flower, brighten the leaves, add a protective golden-green glow, and include small star particles.

Transparent 128×128 canvas.
```

## 81. `bloom-idle-sheet.png`

```text
Create a horizontal four-frame idle sprite sheet for the approved Bloom Guardian.

Show gentle leaf movement, one flower blink or pulse, a soft shield-like glow, and return to the base pose. Keep the pot stationary.

Four equal 128×128 frames, transparent 512×128 canvas.
```

## 82. `bloom-feed-sheet.png`

```text
Create a horizontal six-frame feeding sprite sheet for the approved Bloom Guardian.

Show a completed sticky note floating toward the flower, being absorbed into the bloom, a flower-opening burst, one proud bounce, and return to Happy.

Six equal 128×128 frames, transparent 768×128 canvas.
```

## 83. `bloom-evolution-reveal.png`

```text
Create a hero evolution illustration for the approved Bloom Guardian.

Show the flower fully opening in a warm orange-and-gold burst, protective leaf shapes spreading outward, completed sticky notes circling it, and soft evolution rays.

Centered on a transparent 512×512 canvas. No text or modal frame.
```

---

# Tier 5 — Golden Pin Tree

## 84. `goldtree-happy.png`

```text
Create the Tier 5 Golden Pin Tree character.

Show a small legendary office tree with a graceful brown trunk, rounded golden-green foliage, subtle pushpin-shaped ornaments, and one small crown-like leaf arrangement at the top.

Place it in the Legendary Pin pot. Give it a wise friendly expression. Transparent 128×128 canvas.
```

## 85. `goldtree-okay.png`

```text
Edit the approved Golden Pin Tree into the Okay mood.

Preserve the exact trunk, foliage, ornaments, crown shape, pot, and lighting. Use a calm neutral expression and slightly softer glow.

Transparent 128×128 canvas.
```

## 86. `goldtree-sleepy.png`

```text
Edit the approved Golden Pin Tree into the Sleepy mood.

Keep the exact design. Lower the outer foliage gently, close the eyes, and reduce the golden shimmer.

Transparent 128×128 canvas.
```

## 87. `goldtree-wilting.png`

```text
Edit the approved Golden Pin Tree into the Wilting mood.

Preserve the character and pot. Slightly lower the foliage clusters, mute the gold-green colors, and use a tired but dignified expression.

Do not show dead branches or falling leaves. Transparent 128×128 canvas.
```

## 88. `goldtree-dormant.png`

```text
Edit the approved Golden Pin Tree into the Dormant mood.

Keep the exact design and pot. Show peaceful closed eyes, subdued golden foliage, and a quiet resting glow.

Do not make it appear damaged. Transparent 128×128 canvas.
```

## 89. `goldtree-thriving.png`

```text
Edit the approved Golden Pin Tree into the Thriving mood.

Preserve the exact design. Make the foliage bright gold-green, illuminate the pushpin ornaments, add a soft legendary aura, and include restrained golden sparkles.

Transparent 128×128 canvas.
```

## 90. `goldtree-idle-sheet.png`

```text
Create a horizontal four-frame idle sprite sheet for the approved Golden Pin Tree.

Show subtle leaf shimmer, a gentle branch sway, one blink, and return to the base pose. Keep the pot and trunk stationary.

Four equal 128×128 frames, transparent 512×128 canvas.
```

## 91. `goldtree-feed-sheet.png`

```text
Create a horizontal six-frame feeding sprite sheet for the approved Golden Pin Tree.

Show a completed sticky note floating into the branches, transforming into a small golden leaf, a gentle legendary shimmer, one proud bounce, and return to Happy.

Six equal 128×128 frames, transparent 768×128 canvas.
```

## 92. `goldtree-evolution-reveal.png`

```text
Create the final legendary evolution illustration for the approved Golden Pin Tree.

Show the tree fully illuminated with golden-green foliage, glowing pushpin ornaments, a crown-like canopy, warm radial light, and completed sticky notes transforming into golden leaves.

Prestigious but calm and professional. Centered on a transparent 512×512 canvas. No text or frame.
```

---

# Plant Codex interface

## 93. `btn-codex.svg`

```text
Create a scalable Plant Codex button background.

Use a warm cream surface, golden-brown border, small green leaf emblem, and subtle book-tab shape. Leave sufficient empty space for HTML button text.

Transparent background, no embedded text.
```

## 94. `codex-slot-empty.png`

```text
Create a locked Plant Codex slot.

Use a warm cream card with muted golden-brown frame, a centered dark plant silhouette, a small lock symbol, and subtle paper texture.

No readable text. Front-facing interface asset.
```

## 95. `codex-slot-unlocked.png`

```text
Create an unlocked Plant Codex slot.

Use the same dimensions and frame as the approved locked slot, but replace the lock treatment with a warm gold highlight, green leaf accents, and an empty central display area for a plant thumbnail.

No text.
```

## 96. `codex-thumb-tier0.png`

```text
Create a compact Codex portrait of the approved Pin Seed.

Show the Happy version centered inside a soft cream circular background with a subtle yellow tier accent.

Square transparent canvas, no label or text.
```

## 97. `codex-thumb-tier1.png`

```text
Create a compact Codex portrait of the approved Desk Cactus.

Show the Happy version centered inside a soft cream circular background with an orange tier accent.

Square transparent canvas, no text.
```

## 98. `codex-thumb-tier2.png`

```text
Create a compact Codex portrait of the approved Quest Fern.

Show the Happy version centered inside a soft cream circular background with a green tier accent.

Square transparent canvas, no text.
```

## 99. `codex-thumb-tier3.png`

```text
Create a compact Codex portrait of the approved Bonsai of Boards.

Show the Happy version centered inside a soft cream circular background with a calm blue tier accent.

Square transparent canvas, no text.
```

## 100. `codex-thumb-tier4.png`

```text
Create a compact Codex portrait of the approved Bloom Guardian.

Show the Happy version centered inside a soft cream circular background with a purple-and-gold tier accent.

Square transparent canvas, no text.
```

## 101. `codex-thumb-tier5.png`

```text
Create a compact Codex portrait of the approved Golden Pin Tree.

Show the Happy version centered inside a soft cream circular background with a premium gold-and-platinum tier accent.

Square transparent canvas, no text.
```

---

# Remaining onboarding illustrations

## 102. `plant-onboarding-step1.png`

```text
Create an onboarding illustration explaining that completing tasks feeds the Office Plant.

Show a completed yellow sticky note moving toward the happy Desk Cactus, followed by a small “food” sparkle and cheerful reaction.

Leave space below for HTML text. Clean 400×300 illustration, no embedded words.
```

## 103. `plant-onboarding-step2.png`

```text
Create an onboarding illustration explaining that completion streaks unlock visual buffs.

Show the Desk Cactus beside a warm glowing desk lamp, small flame-streak icon, and subtle sparkle aura.

Leave space below for HTML text. Clean 400×300 illustration, no embedded words.
```

## 104. `plant-onboarding-step3.png`

```text
Create an onboarding illustration explaining that levels and completed tasks unlock plant evolutions.

Show a simple progression from Pin Seed to Desk Cactus to Quest Fern using warm arrows and gentle golden light.

Leave space below for HTML text. Clean 400×300 illustration, no embedded words.
```

---

# Audio assets

These are not generated through an image generator. Use the following briefs with an audio-generation tool or sound designer.

## 105. `feed-soft.mp3`

```text
Create a very short cozy game reward sound for feeding a friendly office plant.

Use a soft wooden pop, gentle bell note, and tiny leaf-like sparkle. Duration 0.4 to 0.7 seconds. Warm, subtle, office-appropriate, and not distracting.

No voice, music, harsh click, or arcade sound.
```

## 106. `evolution-fanfare.mp3`

```text
Create a cozy RPG evolution fanfare lasting approximately 2.5 seconds.

Use warm marimba, gentle chimes, soft strings, and a small uplifting final note. It should feel rewarding and magical without sounding dramatic, royal, or like a casino reward.

No voice.
```

## 107. `mood-recover.mp3`

```text
Create a gentle mood-recovery sound for a friendly plant returning to health.

Use a soft water-drop tone, warm bell shimmer, and subtle upward musical movement. Duration approximately one second.

Peaceful, encouraging, and non-distracting. No voice.
```

## 108. `ui-panel-open.mp3`

```text
Create a subtle interface-panel opening sound for a cozy productivity RPG.

Use a soft paper movement, quiet wooden tap, and gentle UI chime. Duration 0.4 to 0.8 seconds.

Professional and restrained. No voice or strong bass.
```

---

# Final production order summary

Generate assets in this sequence:

```text
1. Visual style reference
2. Base desk scene
3. Stat panel and vitality UI
4. Mood and stat icons
5. Starter pot
6. Pin Seed
7. Desk Cactus
8. Core feeding and evolution effects
9. Empty-state illustration
10. Remaining desk backgrounds
11. Quest Fern
12. Bonsai of Boards
13. Streak overlays
14. Priority effects
15. Unlockable pots
16. Bloom Guardian
17. Golden Pin Tree
18. Plant Codex
19. Remaining onboarding illustrations
20. Audio assets
```

Do not move to a new plant species until its Happy design, other moods, animations, and evolution illustration have been approved.
