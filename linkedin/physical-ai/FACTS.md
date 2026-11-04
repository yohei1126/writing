# Locked facts for Physical AI LinkedIn EN (2026-11-04)

Source of truth: the published Zenn JA article (`_pr18_src/zenn-source.md`). Produce a **full-length** English LinkedIn article with the same depth and detail as Zenn (not a short summary). Do not add claims that are not in the Zenn article.

## Length
- Full parity with Zenn: every stage's struggle → fix → benefit at Zenn depth.
- Do NOT shorten into a digest or "short English version" framing.

## Structure (match Zenn section order)
1. H1 title, then cover image immediately under the H1.
2. Introduction — course (Physical AI Applied 1 / Matsuo-Iwasawa Lab), task overview, then 0/16 → 3/3 arc. Past tense. Course finished and submitted. Link to Zenn JA is fine; do not call this a short version.
3. Task and prerequisites — stack bullets then public links (same coverage as Zenn subsections).
4. Full path to a working demo — RobOps figure, then nine stages listed.
5. Problems and fixes by stage — nine subsections matching Zenn (stage names, not "Wall N" as primary headings). Include setup photos in stages 2 and 3 as below.
6. If you try the same thing.
7. Closing.

## Images (required; relative paths from this article file)
Place these markdown images at the same narrative points as Zenn:
1. Cover (right after H1): `![Cover: SO-ARM101 desk setup for sponge pick-and-place](../../images/physical-ai-linkedin-cover.jpg)`
2. RobOps flywheel (in "Full path to a working demo", where Zenn has the diagram): `![RobOps improvement flywheel: setup, data, training, real-robot evaluation](../../images/physical-ai-roboops-architecture.en.png)`
3. Desk layout (in stage 2 机上配置 / Desk layout standardization, where Zenn has the first setup photo): `![Desk layout with masking-tape frame, sponge, and paper target](../../images/zenn-setup-a.jpeg)`
4. Preflight / framing (in stage 3 事前点検, where Zenn has the second setup photo): `![Top and wrist camera framing of sponge, paper, and follower arm](../../images/zenn-setup-b.jpeg)`
5. Simulation (in stage 7 Simulation evaluation): `![MuJoCo simulation rollout (top + wrist view): arm approaching the object](../../images/physical-ai-sim-mujoco-rollout.jpg)`

Do not invent extra figures. Do not use remote Zenn CDN URLs; use the local `../../images/...` paths above.

## Omit
- Do NOT mention Zennfes, Autumn 2026, or any contest/theme.
- A link to the Japanese Zenn article itself is fine.

## Locked facts
- Course: Physical AI Applied 1, UTokyo Matsuo-Iwasawa Lab. Final assignment, already submitted. Use past tense.
- Task: pick a sponge with the gripper, carry it to a target sheet of paper, place it still.
- Robot: SO-ARM101, 6-DoF low-cost open-source arm, Leader/Follower pair ([LeRobot SO-101 docs](https://huggingface.co/docs/lerobot/so101)).
- Stack: LeRobot, ACT (Action Chunking with Transformers), MuJoCo. Training on a MacBook Pro (M4) with PyTorch MPS, 25,000 steps, about 3.5 to 4 hours, no cloud GPU.
- Cameras: Top = Logicool C920, fixed 16 cm from the right front edge of the desk. Wrist = follower gripper camera. Mac/iPhone Continuity Camera could take priority and shift indices.
- Preflight script: checks fixed serial ports and camera indices, returns `RESULT: PASS` or `FAIL`. No port guessing. Voltage is a visual pre-work checklist item, not part of the script.
- Power: 5V vs 12V confusion. The control board LED lit over USB bus power even without the 12V DC jack connected (false "powered" cue).
- Layout: masking-tape frame on the work mat. Arm base to sponge center 140 mm, arm base to paper center 70 mm (not "the sponge is 140 mm"). Final layout series: layout39. Before this, the sponge and paper target dimensions were changed several times early on, which made coordinate systems inconsistent across datasets. A joint also touched the stand leg at the end of motion before the redesign.
- Teleoperation: after about 20 consecutive episodes, `shoulder_lift` tracking lag grew from about 1.5° to 10-12° (servo heat suspected). Rest roughly every 10 episodes. Standardized start/end wait protocol.
- Data QC: `nohup` recording sessions ended abnormally, so recording moved to the foreground in an interactive terminal. A relative path once appended new episodes to an old dataset, so scripts use absolute paths and stop if the directory is missing or metadata mismatches. QC tool plots joint angles and camera video to find outliers.
- Training: macOS default Bash 3.2 syntax limits caused script trouble; scripts were adjusted.
- Simulation (MuJoCo): box-snap produced false-positive successes; removed in favor of physical-contact judging. Sim success was 25 mm position / 15° angle, which differed from the real visual criterion (grasp and place without dropping). TE = Temporal Ensembling (NOT task engineering): weighted averaging of overlapping predicted action chunks. Too-strong TE smoothing, combined with real inertia and latency, made the arm stall short of the target; the setting was adjusted.
- Checkpoint: the lowest `val_l1` checkpoint (`best_model`) made the real arm tremble and not reach the sponge. Candidates (between 10,000 and 25,000 steps) with a sim success rate were tested on the real robot. `best_model` ranked 6th among all candidates in scoring.
- Real eval: first live eval 0/16 (0%). With the standardized layout and selected layout39 checkpoints, the L2 eval/verification set L2 gave 3/3 grasp-and-place success. Small n: reference value, not a benchmark.
- Nine stages (exact names):
  1. Hardware wiring and power
  2. Desk layout standardization
  3. Preflight (ports + cameras) and framing checks
  4. Teleoperation recording
  5. Data QC
  6. Policy training (Mac MPS / ACT)
  7. Simulation evaluation
  8. Checkpoint selection
  9. Real-robot autonomous evaluation
- Links to keep:
  - Repo: https://github.com/yohei1126/lerobot-so101-pick-and-place
  - Docs: https://yohei1126.github.io/lerobot-so101-pick-and-place/
  - YouTube: https://youtu.be/hYQggz5CilA
  - HF SO-101: https://huggingface.co/docs/lerobot/so101
  - Zenn: https://zenn.dev/yohei/articles/2026-11-03-so101-sponge-paper-real-robot-walls
- Forbidden: invented numbers or claims; tables, HTML, Mermaid; em dashes; music credit; present progressive as if the course were ongoing; calling the piece a "short" version.
