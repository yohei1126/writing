# Locked facts for Physical AI LinkedIn EN (2026-11-03)

- Course: Physical AI Applied 1, UTokyo Matsuo–Iwasawa Lab (already submitted; past tense).
- Task: pick sponge with gripper, place on paper sheet.
- Robot: SO-ARM101 Leader/Follower (LeRobot SO-101 docs https://huggingface.co/docs/lerobot/so101).
- Stack: LeRobot, ACT, Mac MPS ~25k steps ~3.5–4h.
- Cameras: Top = Logicool C920; Wrist = follower gripper camera. Continuity Camera can shift indices.
- Preflight: PASS/FAIL on fixed serial ports + camera index. Voltage = visual checklist only (not in script).
- Layout: layout39 final standardized layout. Arm base → sponge center 140 mm; arm base → paper center 70 mm (tape jig). Not “sponge is 140 mm”.
- First real eval: 0/16. Later reference: L2 eval / verification set L2 → grasp-and-place 3/3 (small n; reference not benchmark).
- TE = Temporal Ensembling (NOT task-engineering). Strong TE smoothing on real robot contributed to stalling / glue-like stop before target.
- Servo heat: ~1.5° → 10–12° tracking error after ~20 episodes; cool ~every 10 episodes.
- Checkpoint: best val_l1 (best_model) ranked ~6th in offline real-task scoring; pick by offline score not val_l1 alone.
- Sim: MuJoCo; box-snap false positives; sim success 25 mm / 15° vs visual place on real robot.
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
- Links to keep: https://github.com/yohei1126/lerobot-so101-pick-and-place ; https://yohei1126.github.io/lerobot-so101-pick-and-place/ ; https://youtu.be/hYQggz5CilA ; https://huggingface.co/docs/lerobot/so101 ; https://zenn.dev/yohei/articles/2026-11-03-so101-sponge-paper-real-robot-walls
- Forbidden: invent numbers/claims; tables/HTML/Mermaid; music credit; present progressive as if course ongoing.

## Also true (from JA Zenn / prior draft; restore if missing)
- Power: confused 5V vs 12V; servo board LED could light without 12V DC (false "powered" cue).
- Cameras: top/wrist indices swapped across runs; Continuity Camera can appear and shift indices.
- Layout history: physical layout changed three times before layout39; earlier changes invalidated prior data for ACT.
- Process accidents: nohup training wrote output somewhere unexpected; relative paths resolved from wrong cwd → prefer absolute paths and cwd check before long runs.
- Offline checkpoint scoring: best_model (best val_l1) ranked about sixth on real-task offline scoring.
