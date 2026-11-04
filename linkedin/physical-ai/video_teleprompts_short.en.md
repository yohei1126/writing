<!-- markdownlint-disable MD013 MD024 MD033 MD034 MD060 -->

# Physical AI SO-101 Pick-and-Place: On-Screen Teleprompt Script (Short Cut, ~106 s, English)

## 1. Purpose and structure

This document is the locked on-screen text and timeline spec for the public English YouTube version (about 106 s) of the Physical AI Applied 1 project video. It is the English companion to the LinkedIn EN article and follows the structure and timing of the Japanese short teleprompt spec exactly.

The video condenses the following: the social context of precision handling at ports, the standardized 140×70 cm desk setup, real-robot layout photos, the RobOps pipeline and local training environment, Temporal Ensembling (TE) closed-loop behavior in MuJoCo simulation, quantitative results, the real-robot SO-101 layout39 rollout, and the main parts of the public repository. The course was finished and submitted, so all copy is in the past tense.

The export is silent: no narration, no music in the file, and no music credit anywhere on screen. Each clip duration below is authoritative. Do not re-measure the footage (ffprobe or similar). Main body total: 105.766 s. There is no extra credit clip at the end.

TE means Temporal Ensembling (not task engineering).

### Clip table and timing

| Shot | Content | Duration | Cumulative | Material |
|---|---|---|---|---|
| A Title | Project title, course info, author, date | 10.000 s | 0.000-10.000 s | Title card (black background / course name, URL, date) |
| B Background → task | Port precision handling context, task and success criteria | 12.000 s | 10.000-22.000 s | Background slide / task definition card |
| C Setup | 140×70 cm standardized desk setup | 8.000 s | 22.000-30.000 s | Setup explanation card / layout diagram |
| C1b Real-robot photos | layout39 real-robot setup photos (2) | 10.000 s | 30.000-40.000 s | Two photos (IMG_1336 / IMG_1338, about 5 s each) |
| C2 Pipeline + training environment | Contract, QC, CI, auto evaluation, plus M4 Pro / MPS | 14.000 s | 40.000-54.000 s | RobOps system diagram (simplified video version: report/figures/roboops_system_architecture_teleprompt.en.svg), training environment |
| D Simulation main | ACT × TE closed-loop motion (0.5x speed) | 17.333 s | 54.000-71.333 s | Representative rollout video (source 8.667 s played at 0.5x) |
| E Quantitative results | TE vs chunk30 comparison table | 12.000 s | 71.333-83.333 s | Quantitative results card (report chapter 5 table) |
| F Real-robot rollout | layout39 TE on the real robot | 12.433 s | 83.333-95.766 s | Real-robot live footage (IMG_1353) |
| G Project repository | Repository components and GitHub URL | 10.000 s | 95.766-105.766 s | Repository card (main components plus public URL) |
| **Total** | | **105.766 s** | **~105.8 s (~106 s)** | |

---

## 2. Per-shot teleprompt spec

### A Title card (0.000-10.000 s / 10.0 s)

| No. | Display window | On-screen text | Focus | Notes |
|---|---|---|---|---|
| A1 | 0.000-10.000 s (10.0 s) | UTokyo Matsuo-Iwasawa Lab: Physical AI Applied 1, Intelligent Robotics 2026 Summer<br>SO-101 Pick-and-Place with ACT and Temporal Ensembling<br>Author yohei1126 / Date 2026/10/31<br>https://weblab.t.u-tokyo.ac.jp/lecture/course-list/physical-ai/advanced1/ | Course name, project title, author, date, and course URL. | Multi-line, centered. Black or dark background for legibility. |

### B Social context and success criteria (10.000-22.000 s / 12.0 s)

| No. | Display window | On-screen text | Focus | Notes |
|---|---|---|---|---|
| B1 | 10.000-16.000 s (6.0 s) | [Social context] Automating precision handling at ports and maritime sites<br>- Repetitive work in hazardous spaces and a shortage of skilled workers<br>- Pallet alignment with tight tolerances and high failure cost, reduced to a tabletop mock-up | Why strict alignment matters on port and shipyard sites, and why a tabletop mock-up is used to cut failure cost. | Show the port context first, following report chapter 1. |
| B2 | 16.000-22.000 s (6.0 s) | [Task & success criteria] Grasp and align in a target frame with SO-101 + ACT<br>- Grasp the object and place it at the target position and orientation<br>- Criteria: alignment rate ≥ 85%, position error < 25 mm, \|yaw\| < 15 deg | How strict the quantitative pass/fail criteria are: under 25 mm in position, under 15 deg in angle. | States the pass/fail criteria explicitly. |

### C Real-robot setup layout (22.000-30.000 s / 8.0 s)

| No. | Display window | On-screen text | Focus | Notes |
|---|---|---|---|---|
| C1 | 22.000-30.000 s (8.0 s) | [Experiment setup] SO-101 desk setup (standardized 140×70 cm layout)<br>- SO-101 arm (6-DoF) + two cameras: Top (Logicool C920) and Wrist<br>- Physical guides for repeatable placement, plus a preflight check | Two-view observation (Top and Wrist), and the 140×70 cm physical guides that keep real-robot runs repeatable. | Gives the setup overview and placement rules. |

### C1b Real-robot photos (30.000-40.000 s / 10.0 s)

| No. | Display window | On-screen text | Focus | Notes |
|---|---|---|---|---|
| C1b | 30.000-40.000 s (10.0 s) | [Real-robot layout] layout39 setup photos (2)<br>- Photo 1 (30.000-35.000 s): overall view, Top camera placement (report/figures/setup_layout39_IMG_1336.jpg)<br>- Photo 2 (35.000-40.000 s): close-up of arm tip and workspace (report/figures/setup_layout39_IMG_1338.jpg) | The actual SO-101, physical guides, and Top/Wrist camera arrangement. | Show `report/figures/setup_layout39_IMG_1336.jpg` for about 5 s, then `report/figures/setup_layout39_IMG_1338.jpg` for about 5 s. Layout39: arm base to sponge center 140 mm, arm base to paper center 70 mm. |

### C2 RobOps pipeline and training environment (40.000-54.000 s / 14.0 s)

| No. | Display window | On-screen text | Focus | Notes |
|---|---|---|---|---|
| C2 | 40.000-54.000 s (14.0 s) | [RobOps pipeline & training environment] Single contract, quality gates, local training<br>1. Contract SSOT: contract.yaml (images, joints, inference parameters in one place)<br>2. Quality QC: rosbag2→LeRobot conversion, dropped-frame and joint-range checks<br>3. Auto evaluation: GitHub Actions CI + MuJoCo closed-loop evaluation<br>4. Training: MacBook Pro M4 Pro / 24 GB RAM / MPS / Metal / PyTorch | One config contract (SSOT) driving data validation, CI, and simulation evaluation, plus local training on M4 Pro / MPS. | Use the simplified video diagram (report/figures/roboops_system_architecture_teleprompt.en.svg). The detailed version (figures/roboops_system_architecture.svg) is for the report only. |

### D Simulation main (54.000-71.333 s / 17.333 s)

Note: the 8.667 s source clip plays at 0.5x (17.333 s). Always label this footage as simulation. The simulated object is a grey box, so say "object" or "target object" and do not call it a yellow sponge.

| No. | Display window | On-screen text | Focus | Notes |
|---|---|---|---|---|
| D1 | 54.000-58.000 s (4.0 s) | [Simulation] ACT × Temporal Ensembling (TE) inference (0.5x speed)<br>- MuJoCo closed-loop environment (chunk_size=30, n_action_steps=1)<br>- Time-weighted averaging of past action predictions for smooth control | Smoother trajectories and less jitter from TE inference. | Section label at top or top-left, detail text at the bottom. |
| D2 | 58.000-63.000 s (5.0 s) | [Grasp] Approaching and grasping the target object<br>- Two-camera image feedback for grasping | Controlled approach speed and a stable gripper grasp. | Covers the moment of grasp. |
| D3 | 63.000-68.000 s (5.0 s) | [Alignment] Matching yaw to the target frame for precise placement<br>- Correcting posture to the frame orientation, not only position | Fine adjustment of entry angle (yaw) into the frame and the placement motion. | Alignment segment. |
| D4 | 68.000-71.333 s (3.333 s) | [Aligned] Precise placement in the target frame achieved<br>- Position error 18.081 mm / \|yaw\| 11.830 deg, criteria met | Placement accuracy at the final resting state. | Hold the final frame as a still. |

### E Quantitative results (71.333-83.333 s / 12.0 s)

| No. | Display window | On-screen text | Focus | Notes |
|---|---|---|---|---|
| E1 | 71.333-83.333 s (12.0 s) | [Quantitative results] Simulation closed-loop evaluation (post50)<br>- TE (n_action_steps=1): alignment rate 1.000 / mean position error 18.081 mm / mean \|yaw\| 11.830 deg<br>- Recheck (seed=1000, 50 ep): alignment rate 1.000 / mean position error 18.283 mm<br>- chunk30 (open-loop): alignment rate 0.000 / mean position error 39.157 mm<br>⇒ All criteria met (alignment rate ≥ 85%, position error < 25 mm, \|yaw\| < 15 deg) | Large gain from TE (alignment rate 0.000 → 1.000, position error 39.157 mm → 18.081 mm) and full reproduction on an independent seed (seed=1000, 50 ep). | Show the report chapter 5 comparison table as the background. |

### F Real-robot rollout (83.333-95.766 s / 12.433 s)

| No. | Display window | On-screen text | Focus | Notes |
|---|---|---|---|---|
| F1 | 83.333-95.766 s (12.433 s) | [Real-robot evaluation] SO-101 rollout (2026-10-30, layout39 TE)<br>- Model: layout39 × Temporal Ensembling (TE)<br>- From Top/Wrist camera images, grasped the sponge and placed it on the target paper in the real world | Successful grasp and place under real lighting and desk reflections, and TE inference validated in simulation carried over to the real robot. | Real-robot footage (IMG_1353), shown under live Top/Wrist video. No idle segments. |

### G Project repository (95.766-105.766 s / 10.0 s)

| No. | Display window | On-screen text | Focus | Notes |
|---|---|---|---|---|
| G1 | 95.766-105.766 s (10.0 s) | [Project repository]<br>- ACT training and inference / Temporal Ensembling (TE)<br>- MuJoCo simulation closed-loop evaluation<br>- contract.yaml (contract SSOT)<br>- rosbag2→LeRobot conversion and quality QC<br>- GitHub Actions CI<br>- SO-101 pick-and-place implementation<br>https://github.com/yohei1126/lerobot-so101-pick-and-place | The public repository: implementation code, contract definition (contract.yaml), evaluation scripts, and CI automation. | Black background. Show main components with the URL. |

---

## 3. Off-screen editor notes (never on screen)

The items below are for editors and publishing checks only. **Do not show any of them in the video.**

1. **Publishing settings**
   - Visibility: YouTube Unlisted or Public, as decided at upload.
   - Audience: "No, it's not made for kids" (Not made for kids).
   - Age restriction: none.
   - Premiere: off.
2. **Privacy**
   - Do not include full name, affiliation, personal email, glimpses of living space, or OS/Finder personal path information.
   - The only person identifier on screen is `yohei1126`.
   - Do not put management instructions such as "unlisted / no personal data / identifier is yohei1126 only" into any on-screen text.
3. **Audio and playback**
   - The export is silent: no narration and no BGM in the file.
   - Background music is added later in YouTube Studio. Do not put any music title, artist, license, or credit in the video, the teleprompts, or the copy-paste blocks.
   - No idle or static filler segments.
4. **Timing**
   - Clip durations in this spec are authoritative. Do not re-measure (ffprobe or similar).
   - Main body is 105.766 s. Do not add a credit clip.
5. **Framing**
   - Public companion to the LinkedIn EN article. Keep the course credit on the title card only.
   - Keep all copy in the past tense (course finished and submitted).

---

## 4. Copy-paste teleprompt strings (A-G / C1b)

Text blocks for pasting directly into an editor (Premiere Pro, DaVinci Resolve, Final Cut Pro, CapCut, etc.).

### Shot A: Title card (0.000-10.000 s)

```text
UTokyo Matsuo-Iwasawa Lab: Physical AI Applied 1, Intelligent Robotics 2026 Summer
SO-101 Pick-and-Place with ACT and Temporal Ensembling
Author yohei1126 / Date 2026/10/31
https://weblab.t.u-tokyo.ac.jp/lecture/course-list/physical-ai/advanced1/
```

### Shot B: Social context and success criteria (10.000-22.000 s)

```text
[Social context] Automating precision handling at ports and maritime sites
- Repetitive work in hazardous spaces and a shortage of skilled workers
- Pallet alignment with tight tolerances and high failure cost, reduced to a tabletop mock-up
```

```text
[Task & success criteria] Grasp and align in a target frame with SO-101 + ACT
- Grasp the object and place it at the target position and orientation
- Criteria: alignment rate ≥ 85%, position error < 25 mm, |yaw| < 15 deg
```

### Shot C: Real-robot setup layout (22.000-30.000 s)

```text
[Experiment setup] SO-101 desk setup (standardized 140×70 cm layout)
- SO-101 arm (6-DoF) + two cameras: Top (Logicool C920) and Wrist
- Physical guides for repeatable placement, plus a preflight check
```

### Shot C1b: Real-robot setup photos (30.000-40.000 s)

```text
[Real-robot layout] layout39 setup photos (2)
- Photo 1 (30.000-35.000 s): overall view, Top camera placement (report/figures/setup_layout39_IMG_1336.jpg)
- Photo 2 (35.000-40.000 s): close-up of arm tip and workspace (report/figures/setup_layout39_IMG_1338.jpg)
```

### Shot C2: RobOps pipeline and training environment (40.000-54.000 s)

```text
[RobOps pipeline & training environment] Single contract, quality gates, local training
1. Contract SSOT: contract.yaml (images, joints, inference parameters in one place)
2. Quality QC: rosbag2→LeRobot conversion, dropped-frame and joint-range checks
3. Auto evaluation: GitHub Actions CI + MuJoCo closed-loop evaluation
4. Training: MacBook Pro M4 Pro / 24 GB RAM / MPS / Metal / PyTorch
```

### Shot D: Simulation main (54.000-71.333 s)

```text
[Simulation] ACT × Temporal Ensembling (TE) inference (0.5x speed)
- MuJoCo closed-loop environment (chunk_size=30, n_action_steps=1)
- Time-weighted averaging of past action predictions for smooth control
```

```text
[Grasp] Approaching and grasping the target object
- Two-camera image feedback for grasping
```

```text
[Alignment] Matching yaw to the target frame for precise placement
- Correcting posture to the frame orientation, not only position
```

```text
[Aligned] Precise placement in the target frame achieved
- Position error 18.081 mm / |yaw| 11.830 deg, criteria met
```

### Shot E: Quantitative results (71.333-83.333 s)

```text
[Quantitative results] Simulation closed-loop evaluation (post50)
- TE (n_action_steps=1): alignment rate 1.000 / mean position error 18.081 mm / mean |yaw| 11.830 deg
- Recheck (seed=1000, 50 ep): alignment rate 1.000 / mean position error 18.283 mm
- chunk30 (open-loop): alignment rate 0.000 / mean position error 39.157 mm
⇒ All criteria met (alignment rate ≥ 85%, position error < 25 mm, |yaw| < 15 deg)
```

### Shot F: Real-robot rollout (83.333-95.766 s)

```text
[Real-robot evaluation] SO-101 rollout (2026-10-30, layout39 TE)
- Model: layout39 × Temporal Ensembling (TE)
- From Top/Wrist camera images, grasped the sponge and placed it on the target paper in the real world
```

### Shot G: Project repository (95.766-105.766 s)

```text
[Project repository]
- ACT training and inference / Temporal Ensembling (TE)
- MuJoCo simulation closed-loop evaluation
- contract.yaml (contract SSOT)
- rosbag2→LeRobot conversion and quality QC
- GitHub Actions CI
- SO-101 pick-and-place implementation
https://github.com/yohei1126/lerobot-so101-pick-and-place
```
