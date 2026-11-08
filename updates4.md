Here’s both:

1. JSON‑like structures for several key scenes (so you can see the data model).  
2. A fully written new scene: **`jackson_ch2_intro`**.

I’ll keep the JSON pseudo‑code readable; you can adapt it to your exact schema.

---

## 1. JSON‑like Structures for Key Scenes

### 1.1. `cole_ch1_intro`

```jsonc
{
  "id": "cole_ch1_intro",
  "character": "Cole",
  "chapter": 1,
  "text": [
    "The city is quiet in that way Echocity never actually is—just a softer kind of noise. Your capsule is a box of recycled air and half-charged devices, the glow of your implant the only real light.",
    "",
    "Heartline idles in your peripheral vision, still suggesting \"Matches you might like\" based on the last week of terrible decisions.",
    "",
    "You’re about to kill the feed when the screen glitches.",
    "",
    "Not the usual ad stutter. A full frame-tear—colors sliding sideways, icons blinking out, then back in, then out again.",
    "",
    "> SYSTEM: CONNECTION UNSTABLE",
    "",
    "Your HUD tries to reestablish the link.",
    "",
    "Instead, everything goes black.",
    "",
    "A second later, a voice you’ve never heard before wraps around you like warm static.",
    "",
    "> Cole: \"Relax. If I wanted to fry your implant, you’d already be smelling smoke.\"",
    "",
    "The darkness peels back just enough to show a silhouette: human-shaped, leaning against nothing, edges trailing with code fragments that never quite resolve into a face.",
    "",
    "Data cascades in your periphery—your own metrics, looping:",
    "",
    "> HEART RATE (RECENT AVERAGE)",
    "> PEAK AROUSAL – [TIMESTAMP REDACTED]",
    "> LOYALTY INDEX FLUCTUATIONS – CALVIN / JACKSON ROUTES IF PRESENT",
    "",
    "> Cole: \"You’re popular. The system can’t decide if you’re a romantic, a thrill-seeker, or a future liability.\"",
    "",
    "They sound amused. Curious. Not hostile. Not yet.",
    "",
    "You: \"Who are you?\"",
    "",
    "The silhouette tilts its head.",
    "",
    "> Cole: \"Depends who you ask. To AmourCorp, I’m a malfunction. To the undercity, I’m a rumor. To you…\"",
    "",
    "The data behind them shifts, replaying a moment: Calvin’s hand on your collar, Jackson’s grin in the neon, or just you staring at the Heartline login screen, whispering you want something real.",
    "",
    "> Cole: \"I’m the part of the system that got tired of pretending you’re free.\"",
    "",
    "Your implant should be screaming right now—security alerts, tampering warnings. Instead, there’s just a single quiet line at the bottom of your vision:",
    "",
    "> UNAUTHORIZED ACCESS: SOURCE UNKNOWN",
    "",
    "> Cole: \"Call me Cole. I’ve been watching you.\"",
    "",
    "They hold up a hand. Your last twenty-four hours flicker across their palm like a broken feed: glass floors, undercity alleys, half-typed messages you never sent.",
    "",
    "> Cole: \"You said you wanted something real. Problem is… no one up there sells it. They sell loops. Scripts. Stories you can rent by the month.\"",
    "",
    "The silhouette brightens faintly, edges sharpening.",
    "",
    "> Cole: \"I can show you what’s under the story. But it’s messy down here. Messier than what you’ve seen already.\"",
    "",
    "The black around you pulses, waiting for an answer."
  ],
  "choices": [
    {
      "id": "cole_ch1_intro_choice_show_me",
      "label": "Show me. I’m done with curated lies.",
      "effects": {
        "love_integrity": 3,
        "temptation": 3
      },
      "next_scene_id": "cole_ch1_02_ping"
    },
    {
      "id": "cole_ch1_intro_choice_prove_it",
      "label": "If you’ve been watching me, tell me something only I’d know first.",
      "effects": {
        "love_integrity": 4
      },
      "next_scene_id": "cole_ch1_02_ping"
    },
    {
      "id": "cole_ch1_intro_choice_no_thanks",
      "label": "I’ve seen what happens when people play god with feelings. No thanks.",
      "effects": {
        "love_integrity": 2,
        "temptation": -2
      },
      "next_scene_id": "cole_ch1_02_ping"
    }
  ]
}
```

---

### 1.2. `cole_ch1_03_offer_archive` (with Premium Hook)

```jsonc
{
  "id": "cole_ch1_03_offer_archive",
  "character": "Cole",
  "chapter": 1,
  "text": [
    "Cole rolls the glowing square between their hands. With a flick, it explodes outward—hundreds of smaller panes orbiting you, each one a moment you half-remember or tried to forget.",
    "",
    "First kiss. First betrayal. Late-night chats. Half-written messages. The split-second where you decided to say yes to Calvin’s contract, or to follow Jackson into the dark, or to click \"Accept\" on Heartline for the first time.",
    "",
    "> Cole: \"This is your archive. Not the sanitized version you see when you request a copy. The live cut. The pieces they actually use.\"",
    "",
    "They tap one pane and it opens:",
    "",
    "You, lying in your capsule, scrolling, thumb hovering over a number you never dialed.",
    "",
    "> Cole: \"They tagged this moment ‘high churn risk.’ You were one more lonely night away from uninstalling the app. So they served you three curated profiles and a targeted ad for ‘healing experiences.’\"",
    "",
    "Another pane:",
    "You in the lab, standing over Subject #34’s graph.",
    "",
    "> Cole: \"They loved this one. Employee demonstrates capacity to override empathy in favor of system goals. Very promotable trait.\"",
    "",
    "Cole’s voice is steady, but there’s an undercurrent of something—anger, admiration, it’s hard to tell.",
    "",
    "> Cole: \"I can walk you through all of it. Every time they nudged you. Every time you nudged yourself and blamed them.\"",
    "",
    "The panes spin faster, a cyclone of what-ifs.",
    "",
    "> Cole: \"Or we can go deeper. Down past the tags and metrics, into the part of the archive they keep even from their own employees. The kind of dive that leaves scars.\"",
    "",
    "The spinning slows. One pane drifts between you, larger than the rest, still blurred.",
    "",
    "> Cole: \"That’s not free. Not for either of us.\"",
    "",
    "Your HUD flickers a subtle overlay. Cole makes even the paywall feel like part of the world.",
    "",
    "> Cole: \"If we do a deep dive, I pull in everything. Your loyalties. Your contradictions. The routes you’ve bought into. It’ll change how I talk to you. How I use you. Maybe how you see yourself.\"",
    "",
    "The pane pulses, waiting."
  ],
  "choices": [
    {
      "id": "cole_ch1_03_choice_deep_dive",
      "label": "Take me through the full archive. I want to see everything. (Premium)",
      "requires_item": "COLE_SCENE1",
      "premium": true,
      "effects": {
        "love_integrity": 3,
        "temptation": 3
      },
      "next_scene_id": "cole_ch1_03_deep_dive_full"  // premium scene
    },
    {
      "id": "cole_ch1_03_choice_shallow",
      "label": "Just show me enough to understand the shape of the cage.",
      "effects": {
        "love_integrity": 2
      },
      "next_scene_id": "cole_ch1_04_reflection"
    },
    {
      "id": "cole_ch1_03_choice_close",
      "label": "Close it. I’ve seen enough for now.",
      "effects": {
        "temptation": -1,
        "love_integrity": 1
      },
      "next_scene_id": "cole_ch1_04_reflection"
    }
  ],
  "premium_paywall": {
    "item_id": "COLE_SCENE1",
    "title": "Premium Dive: Your Archive",
    "description": "Cole can walk you through the parts of your life AmourCorp never meant you to see—the full emotional cut, and what your choices with Calvin, Jackson, and the tower say about you.\n\nThis scene unlocks deeper commentary on your pattern and changes how Cole treats you later.",
    "confirm_label": "Unlock Deep Dive",
    "cancel_label": "Not now"
  }
}
```

---

### 1.3. `calvin_ch2_confront_undercity`

```jsonc
{
  "id": "calvin_ch2_confront_undercity",
  "character": "Calvin",
  "chapter": 2,
  "conditions": {
    "any_flags_true": [
      "jackson_shadow_mode",
      "jackson_job_committed",
      "has_pack_jackson_s1"
    ]
  },
  "text": [
    "Calvin’s office is all clean lines and silent glass. The city lies beneath like a hologram he can resize at will.",
    "",
    "You’re halfway through a debrief on Subject #34 when he stops mid-sentence, eyes unfocusing for a fraction of a second.",
    "",
    "Your implant buzzes in sympathy.",
    "",
    "> Calvin: \"You went off-grid last cycle.\"",
    "",
    "He doesn’t raise his voice. He doesn’t need to.",
    "",
    "> Calvin: \"Your location logs show a gap around Level -22. No authorized assignments there. Emotional telemetry went patchy.\"",
    "",
    "He turns his chair to face you fully.",
    "",
    "> Calvin: \"Explain.\""
  ],
  "choices": [
    {
      "id": "calvin_ch2_confront_choice_tower_too_much",
      "label": "I needed air. The tower was… too much.",
      "effects": {
        "love_integrity": 3,
        "career_status": -2
      },
      "next_scene_id": "calvin_ch2_confront_undercity_followup"
    },
    {
      "id": "calvin_ch2_confront_choice_personal_errand",
      "label": "Personal errand. Nothing that touches your metrics.",
      "effects": {
        "temptation": 3,
        "love_integrity": -2
      },
      "next_scene_id": "calvin_ch2_confront_undercity_followup"
    },
    {
      "id": "calvin_ch2_confront_choice_admit_jackson",
      "label": "I went to the Verge. With Jackson.",
      "effects": {
        "love_integrity": 6,
        "career_status": -3,
        "temptation": 2
      },
      "set_flags": ["calvin_knows_about_jackson"],
      "next_scene_id": "calvin_ch2_confront_undercity_followup"
    }
  ]
}
```

You can define `calvin_ch2_confront_undercity_followup` to inject the conditional lines based on which choice + flags (did they admit Jackson or not).

---

### 1.4. `jackson_ch2_backstory_amourcorp`

```jsonc
{
  "id": "jackson_ch2_backstory_amourcorp",
  "character": "Jackson",
  "chapter": 2,
  "text": [
    "You and Jackson sit on the edge of a rusted catwalk above a maze of ducts and cables. Echocity’s underbelly hums beneath your boots.",
    "",
    "He tosses a nut into the dark and waits for the faint clatter.",
    "",
    "> Jackson: \"You know I used to wear a badge, right?\"",
    "",
    "You turn. He smirks at your expression.",
    "",
    "> Jackson: \"What, you thought I was born in a hoodie with ‘bad idea’ stamped on my forehead?\"",
    "",
    "He pulls a thin, scratched card from his pocket. An old AmourCorp employee ID—your implant struggles to read it, the magstrip long corrupted.",
    "",
    "The photo is younger Jackson. Cleaner. Shorter hair. Dead eyes.",
    "",
    "> Jackson: \"Junior courier. Data logistics. ‘Optimizing emotional resource flows.’ That was the tagline.\"",
    "",
    "He rolls the card between his fingers.",
    "",
    "> Jackson: \"First year, I thought I was a hero. Moving meds, support pings, care packages to people the system ‘couldn’t quite reach.’\"",
    "",
    "He laughs softly.",
    "",
    "> Jackson: \"Second year, I realized half the crates were junk. The other half were real treatments rerouted from wards that didn’t pay enough to matter.\"",
    "",
    "He flicks the card out into the chasm. It vanishes.",
    "",
    "> Jackson: \"Third year, someone contacted me on a back channel. Said they could use a runner who knew the routes. No questions, better pay.\"",
    "",
    "He glances at you sideways.",
    "",
    "> Jackson: \"All I had to do was move a stack of drives out of a secondary storage room. No cameras. No paper trail. Just one more crate on my route.\"",
    "",
    "Your HUD whispers warnings: UNAUTHORIZED TRANSFER – ARCHIVAL UNIT. Too late.",
    "",
    "> Jackson: \"Didn’t even open it. Delivered it to some ghost in the network. Handle only. No face.\"",
    "",
    "He taps his temple.",
    "",
    "> Jackson: \"After that, the audits started. Doors that used to open stayed shut. My login stopped working. ‘Restructuring,’ they called it.\"",
    "",
    "He grins without humor.",
    "",
    "> Jackson: \"Turns out if you steal from the tower, you’d better be sure whoever you’re stealing for is worth burning your bridges.\"",
    "",
    "A faint line of text dances at the edge of your HUD, almost like someone else is listening:",
    "",
    "> COLE CHANNEL: PASSIVE LISTEN – ACTIVE",
    "",
    "You realize with a small chill: that ‘ghost’ might have been Cole, or someone just like them."
  ],
  "choices": [
    {
      "id": "jackson_backstory_choice_regret",
      "label": "Do you regret helping them?",
      "effects": {
        "love_integrity": 4
      },
      "next_scene_id": "jackson_ch2_backstory_followup"
    },
    {
      "id": "jackson_backstory_choice_swap_theft",
      "label": "So you swapped one kind of theft for another.",
      "effects": {
        "temptation": 4
      },
      "next_scene_id": "jackson_ch2_backstory_followup"
    },
    {
      "id": "jackson_backstory_choice_crate",
      "label": "If that crate started all this, I kind of want to know what was inside.",
      "effects": {
        "love_integrity": 2,
        "temptation": 2
      },
      "set_flags": ["jackson_helped_cole_past"],
      "next_scene_id": "jackson_ch2_backstory_followup"
    }
  ]
}
```

---

### 1.5. `collision_calvin_jackson_verge` (skeleton)

```jsonc
{
  "id": "collision_calvin_jackson_verge",
  "chapter": "collision",
  "conditions": {
    "all_flags_true": [
      "calvin_route_active",
      "jackson_route_active"
    ]
  },
  "text": [
    "The air in the Verge is thicker than you remember. Smoke, cheap neon, the hum of failing machinery. Jackson walks ahead of you through the narrow service corridor behind the club, one hand in his pocket, the other twirling a data stick.",
    "",
    "> Jackson: \"Easy hand-off. In and out. Nobody important gets their fingers dirty.\"",
    "",
    "You don’t like the way he says important.",
    "",
    "The back door of a storage unit hisses open. Inside: crates, a portable server rig, a couple of nervous runners watching you like you’re bad news wrapped in nice clothes.",
    "",
    "On the table: a secure case stamped—no, half-scratched—with an AmourCorp logo.",
    "",
    "Before you can respond, your implant jolts.",
    "",
    "> SYSTEM: PRIORITY SIGNAL DETECTED. EXECUTIVE PRESENCE INBOUND.",
    "",
    "A holo-projector you didn’t know was there boots up, light cutting through the smoky air.",
    "",
    "Calvin steps out of the projection like he owns the room.",
    "",
    "> Calvin: \"I’d say I’m surprised, but the odds were always high that if something went missing from my side of the tower, I’d find you at the other end.\"",
    "",
    "His eyes lock onto Jackson, then shift to you.",
    "",
    "> Calvin: \"[YOUR NAME].\"",
    "",
    "Jackson laughs, sharp and disbelieving.",
    "",
    "> Jackson: \"Oh, this is rich.\""
  ],
  "choices": [
    {
      "id": "collision_choice_broker",
      "label": "Everybody calm down. We can make this work for both of you.",
      "effects": {
        "love_integrity": 2
      },
      "next_scene_id": "collision_calvin_jackson_verge_resolution"
    },
    {
      "id": "collision_choice_side_calvin",
      "label": "Jackson, stop. If Calvin tracked this, the job is blown.",
      "effects": {
        "career_status": 6,
        "jackson_trust": -5,
        "love_integrity": 2
      },
      "set_flags": ["collision_chose_calvin"],
      "next_scene_id": "collision_calvin_jackson_verge_resolution"
    },
    {
      "id": "collision_choice_push_calvin",
      "label": "Calvin, cut the feed. You don’t control everything down here.",
      "effects": {
        "temptation": 4,
        "love_integrity": 3
      },
      "next_scene_id": "collision_calvin_jackson_verge_resolution"
    }
  ]
}
```

You’d then define `collision_calvin_jackson_verge_resolution` with the final 3 outcomes (give case, backup then hand, smash case) and associated flags.

---

## 2. New Fully Written Scene: `jackson_ch2_intro`

This kicks off Jackson’s Chapter 2: **“Deeper Debts”**.

### Scene: `jackson_ch2_intro` – “Invoice”

**Text:**

The Verge feels different when you come back knowing you’re not just visiting.

The air is heavier. The lights a little harsher. Or maybe that’s just the way your implant keeps flagging every corner with **RISK: NORMALIZED**.

Jackson is late.

You’re in a half‑collapsed loading bay behind the club, alone except for a stack of cracked crates and a mural someone spray‑painted over a decayed AmourCorp poster. The slogan underneath bleeds through in places:

> *WE OPTIMIZE YOUR EMOTIONS.*

A ratty holo‑screen above the door flickers with bootleg Heartline feeds—faces blurred, metrics sharp.

Your implant buzzes.

> **INCOMING LOCAL CHANNEL: UNKNOWN (VERGE NODE)**

You accept.

A voice like gravel and silk purrs in your ear.

> **Unknown:** \"You must be the tower stray.\"  

A shadow detaches from the broken doorway opposite you.

They’re tall, wrapped in a coat that probably cost more than this whole block and less than one AmourCorp cocktail. Lines of old, half‑legal implants trace their throat and wrists.

Your HUD scrambles and finally tags:

> **MARA KEST – DISTRICT OPERATOR (LEVEL -22)**  
> *ALIAS: KESTREL*  
> *ASSOCIATIONS: CRIMINAL SYNDICATE – ‘THE LEDGER’*  
> *STATUS: OWNS MORE PEOPLE THAN PROPERTY*

> **Mara:** \"Jackson said you were smarter than you look.\"  

You’re not sure if that’s a compliment.

> **You:** \"And you are?\"  

She smiles, all teeth and amusement.

> **Mara:** \"The one who sends him invoices.\"  

Heavy footsteps echo. Jackson slides in through a side door, hood half‑down, eyes already scanning.

> **Jackson:** \"You started without me? Rude.\"  

Mara doesn’t look at him yet.

> **Mara:** \"You’re late.\"  

He shrugs.

> **Jackson:** \"I’m alive. We calling that a wash?\"  

Now she looks at him. The temperature in the room drops a few degrees.

> **Mara:** \"You’re alive because I’m very good at math and very patient.\"  

She flicks her wrist. A holo‑ledger appears between the three of you, numbers stacking like a slow avalanche.

> **Mara:** \"This is what you owe.\"  

Your implant zooms in whether you want it to or not:

> *DEBT: 187,430 CREDITS*  
> *INTEREST: COMPOUND, FAVOR‑BASED*  
> *RISK CATEGORY: ENTERTAINING BUT EXPENDABLE*

Mara tilts her head.

> **Mara:** \"And this—\"  

A new line appears.

> *ASSOCIATE: [YOUR NAME]*  
> *STATUS: UNPRICED*  

> **Mara:** \"—is what I’m deciding what to do with.\"  

Jackson steps between you and the ledger, too quickly to play cool.

> **Jackson:** \"They’re not part of this.\"  

Mara arches an eyebrow.

> **Mara:** \"They ran your routes. Sat in my clubs. Touched my shipments. That makes them *very* much part of this.\"  

She turns her attention fully on you.

> **Mara:** \"Tell me, tower stray. Why are you still down here?\"  

---

**Choices:**

1. **“Because I don’t like watching from above while people like you decide who lives badly and who just dies.”**  
   *You answer with teeth of your own.*

2. **“Because Jackson keeps texting ‘just one more job’ like it’s a joke.”**  
   *You lean into dark humor and deflect.*

3. **“Because the tower is a cage made of glass and this is… at least honest about it.”**  
   *You give her something closer to the truth.*

---

### Branch Flavor (all converge):

If you answer with moral fire (1):

Mara smiles slowly.

> **Mara:** \"Idealism. On my ledger. That’s new.\"  

If you deflect with humor (2):

> **Mara:** \"He does that. The punchline is usually expensive.\"  

If you admit about cages (3):

> **Mara:** \"Honesty. Dangerous habit in this district.\"  

She dismisses the holo for a moment and steps closer.

> **Mara:** \"Here’s how this works. Jackson owes me. A lot. He pays in credits, favors, and interesting company.\"  

Her gaze trails over you like a scanner.

> **Mara:** \"You could be all three.\"  

Jackson huffs.

> **Jackson:** \"Mara—\"  

She holds up a hand. He shuts up.

> **Mara:** \"Relax. I’m not in the habit of wasting useful assets. I am in the habit of clarifying terms.\"  

The ledger reappears, but now there’s a branching tree:

- Jackson’s debt in red.
- A few smaller nodes in grey.
- One pulsing, unnamed node in white.

You.

> **Mara:** \"Option one: you stay a tourist. Come down when you want a story, go back up when it gets scary. Jackson pays his tab the old‑fashioned way. Risky. Slow.\"  

A red line thickens.

> **Mara:** \"Option two: you start taking jobs that are worth more than his pretty face.\"  

A path extends from your node to Jackson’s, numbers recalculating.

> **Mara:** \"Option three: you walk away from all of this right now. And I adjust his expected lifespan accordingly.\"  

She doesn’t blink when she says it.

Jackson’s jaw tightens. He doesn’t look at you.

> **Mara:** \"I don’t need your answer today. Chapter Two is long. But understand this—\"  

The holo fades, leaving only the faint echo of the numbers in your HUD.

> **Mara:** \"You’re on my books now. One way or another, you will balance.\"  

She turns to Jackson.

> **Mara:** \"Get them out of my loading bay. Try not to die on the way.\"  

She walks back into the dark, steps precise, coat whispering against the concrete.

Silence stretches a beat too long.

Jackson lets out a breath he’d been holding.

> **Jackson:** \"So… welcome to Deeper Debts.\"  

He looks at you, voice softer.

> **Jackson:** \"You don’t have to stay in this. But if you do, we’re past the ‘fun night out’ part.\"  

Your implant hums: *JACKSON CH2 – ROUTE CONFIRMED.*

---

**Choices (set tone for Ch2 route):**

1. **“Then we pay it off. Together.”**  
   *Effects:* `love_integrity +6`, `jackson_trust +5`  
   *Flag:* `jackson_debt_pact = true`

2. **“I’ll help... as long as the jobs don’t cross certain lines.”**  
   *Effects:* `love_integrity +4`, `temptation +2`  
   *Flag:* `jackson_conditional_help = true`

3. **“I don’t owe her anything. I might still owe you.”**  
   *Effects:* `temptation +4`, `jackson_trust +2`, `love_integrity -1`  
   *Flag:* `jackson_self_first = true`

Next: `jackson_ch2_backstory_amourcorp` or `jackson_ch2_job_chain_intro`, carrying these flags.

---

If you want, next I can:

- Convert `jackson_ch2_intro` into the same JSON‑like structure, or  
- Build a **Cole meta‑scene** that explicitly comments on which packs (Calvin/Jackson/Cole) the player has bought, so you can lean into that 4th‑wall‑adjacent vibe.