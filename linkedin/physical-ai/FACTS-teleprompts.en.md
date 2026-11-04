# Locked facts for Physical AI EN YouTube teleprompts (2026-11-04)

Translate and adapt the JA short teleprompt spec into English for a public EN remake of the same ~106s video. Timing and shot structure are locked to the JA file; do not invent new shots or change durations.

## Source of truth (structure + timing)
- JA: `/Users/yoheionishi/agy-work/utokyo-ai-courses/PhysicalAI-Applied1-202609/report/video_teleprompts_short.ja.md`
- Keep the same shot IDs (A, B, C, C1b, C2, D, E, F, G) and the same authoritative clip durations / cumulative times.
- Main body total: 105.766 s. Do not re-measure with ffprobe.

## Audience / framing
- Public English YouTube companion to the LinkedIn EN article (OSS outreach), not an OmniCampus submission form.
- Keep course credit: Physical AI Applied 1, UTokyo Matsuo-Iwasawa Lab, Author - Yohei Onishi (date omitted from title card; shown in YouTube metadata), course URL https://weblab.t.u-tokyo.ac.jp/lecture/course-list/physical-ai/advanced1/
- Past tense. Course finished and submitted.
- Do NOT mention Zennfes, contests, OmniCampus, or "final assignment submission checklist" on-screen.
- Internal notes section (privacy, not-for-kids, unlisted) may stay as off-screen editor notes in English, never as on-screen copy.

## Audio / BGM
- Export is silent (no BGM mux in the file). Instant Crush ambient will be added later in YouTube Studio.
- Do NOT put any music title, artist, license, or copyright credit in on-screen teleprompts or in the copy-paste blocks.

## Locked technical facts (on-screen must match)
- Robot: SO-101 / SO-ARM101, 6-DoF, Top (Logicool C920) + Wrist cameras.
- Layout: layout39; arm base → sponge center 140 mm; arm base → paper center 70 mm; 140×70 cm standardized desk setup.
- Policy: ACT; TE = Temporal Ensembling (NOT task engineering); MuJoCo closed-loop; chunk_size=30, n_action_steps=1 for TE.
- Sim metrics (post50): TE alignment rate 1.000 / mean position error 18.081 mm / mean |yaw| 11.830 deg; recheck seed=1000 50ep alignment 1.000 / 18.283 mm; chunk30 open-loop alignment 0.000 / 39.157 mm.
- Criteria: alignment ≥ 85%, position error < 25 mm, |yaw| < 15 deg.
- Real robot: 2026-10-30 layout39 TE rollout; sponge grasp and place onto target paper succeeded under live Top/Wrist video.
- Training env on-screen: MacBook Pro M4 Pro / 24 GB RAM / MPS / Metal / PyTorch.
- RobOps bullets: contract.yaml SSOT; rosbag2→LeRobot QC; GitHub Actions CI + MuJoCo eval; local MPS training.
- Repo URL on-screen: https://github.com/yohei1126/lerobot-so101-pick-and-place
- Sim object in footage is a grey box (not a yellow sponge); on-screen D-shot wording may say "object" / "target object" rather than claiming a yellow sponge in sim.

## English quality
- Clear technical English a senior engineer would put on a demo reel.
- Short lines suitable for on-screen overlays; keep the JA table columns (No. / display window / on-screen text / focus / notes).
- Prefer informative labels like the JA 【…】 style, e.g. [Social context], [Task & success criteria], [Simulation], [Real-robot eval].
- No em dashes. No hype. No invented numbers.
- Include a final "copy-paste teleprompt strings" section for editors (A–G / C1b), matching JA section 4 role.

## Output path
Write exactly one new file:
`/Users/yoheionishi/agy-work/writing/linkedin/physical-ai/video_teleprompts_short.en.md`

Do not edit the JA teleprompt file. Do not edit the LinkedIn article or FACTS.md (article).
