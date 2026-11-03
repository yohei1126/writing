# From 0/16 to a working sponge place: nine stages of imitation learning on a desktop robot arm

My first live evaluation of an imitation-learning policy on a real robot arm scored 0/16. The arm trembled and stopped short of the target, or the gripper closed on nothing, again and again.

The model was not the main problem. The rest of the loop was: wiring, power, camera indices, desk layout, servo heat, simulation criteria, smoothing settings, and how I chose checkpoints. After I fixed those, a later policy completed grasp-and-place 3 out of 3 times on the L2 evaluation set (verification set L2). With n=3, that is a reference point, not a benchmark.

I did this as the final assignment for Physical AI Applied 1 at the UTokyo Matsuo-Iwasawa Lab. The course has finished and the assignment is submitted. This is a short English version of my [Japanese write-up on Zenn](https://zenn.dev/yohei/articles/2026-11-03-so101-sponge-paper-real-robot-walls).

## The task and the stack

The task: pick a sponge with the gripper, carry it onto a target sheet of paper, and set it down still.

- Robot: SO-ARM101, a low-cost open-source 6-DoF desktop arm, built as a Leader/Follower pair. A person moves the leader arm, and the follower copies it ([LeRobot SO-101 docs](https://huggingface.co/docs/lerobot/so101)).
- Learning method: imitation learning from teleoperated demonstrations (camera images plus joint angles).
- Framework and policy: LeRobot and ACT (Action Chunking with Transformers), which predicts several future steps at once.
- Simulator: MuJoCo.
- Cameras: a Logicool C920 as the top camera and the follower's gripper camera as the wrist camera.
- Training: a MacBook Pro (M4) with PyTorch MPS, 25,000 steps, about 3.5 to 4 hours. No cloud GPU.

Everything is public: the [repository](https://github.com/yohei1126/lerobot-so101-pick-and-place), the [docs](https://yohei1126.github.io/lerobot-so101-pick-and-place/), and a [demo video on YouTube](https://youtu.be/hYQggz5CilA).

## Training was one of nine stages

Getting to a working demo took a loop of nine stages, not just model training:

1. Hardware wiring and power
2. Desk layout standardization
3. Preflight (ports + cameras) and framing checks
4. Teleoperation recording
5. Data QC
6. Policy training (Mac MPS / ACT)
7. Simulation evaluation
8. Checkpoint selection
9. Real-robot autonomous evaluation

Training was stage 6. Most of the problems below came from the other eight. Each one was a physical or procedural wall, and each fix came from the desk, not the model.

## Wall 1: I confused 5V and 12V

I mixed up the 5V and 12V supplies, and I swapped the leader and follower serial ports. The control board LED lit up on USB bus power even when the 12V DC jack was not connected. It looked powered when it was not.

I plugged in one USB adapter at a time to fix the port names and labeled the cables. I turned power-up into a checklist and confirmed the 12V plug by eye. The preflight script no longer guesses ports. It only checks the fixed ones. That removed the startup port errors and the under-powered servo errors.

## Wall 2: the desk layout kept changing

At the end of a motion, an arm joint touched the leg of the stand. Early on, I also changed the sponge and paper positions several times, so datasets no longer shared a coordinate system.

I redesigned the layout to keep clear of the arm's range and fixed one spec. The arm base to sponge center distance was 140 mm, and the arm base to paper center distance was 70 mm. I marked it with masking tape on the work mat as a physical jig. The final layout series was layout39. With one fixed layout, the contact accidents stopped and the data became reproducible.

## Wall 3: cameras and ports shifted under me

The top and wrist camera indices swapped after reboots and USB replugs. On a Mac, Continuity Camera with an iPhone could also show up as a preferred device and shift the indices.

I turned off the automatic phone camera handoff in the OS settings. I fixed the top camera 16 cm from the right front edge of the desk. Then I wrote a preflight script that checks the serial ports and camera indices and returns FAIL if anything is off or an unexpected camera appears. I do not start recording until it prints PASS. Voltage stayed on a visual checklist, because the script cannot see it.

## Wall 4: servo heat during teleoperation

After about 20 episodes in a row, the follower's shoulder_lift joint lagged its command by 10 to 12° instead of about 1.5°. I suspected servo heat. Setup and teardown also varied from episode to episode, which made trajectories uneven.

I paused about every 10 episodes to let the servos cool. I also standardized the procedure and the waiting time before and after each episode. Tracking lag stopped growing, and the demonstrations stayed consistent.

## Wall 5: recording accidents and data QC

Recording sessions run with nohup ended abnormally. A relative path once made me append new episodes to an old dataset.

I moved recording to the foreground in an interactive terminal. Scripts now use absolute paths and stop if the directory is missing or the metadata does not match. I also built a QC tool that plots joint angles and camera video so I could remove outliers before training.

## Wall 6: training without a cloud GPU

I had a MacBook Pro (M4) and no NVIDIA GPU. To avoid renting cloud GPUs and uploading large video datasets each time, I kept recording, training, and checking on one Mac, using the PyTorch MPS backend. The 25,000-step run took about 3.5 to 4 hours. macOS ships Bash 3.2, which broke some of my script syntax, so I adjusted the scripts until the whole loop ran on the stock environment.

## Wall 7: simulation told me what I wanted to hear

In MuJoCo, a box-snap shortcut counted a placement as a success once the object came close enough, even when the real robot would not have grasped it. The simulation also judged success by position within 25 mm and angle within 15°. My real test was visual: grasp the sponge and set it down in the target area without dropping it.

I removed box-snap and judged success only by physical contact. I also revisited Temporal Ensembling (TE), which averages overlapping predicted action chunks to smooth motion. With strong TE smoothing, plus the real arm's inertia and communication delay, the arm stopped short of the target. I tuned TE to suit the real arm. A stricter simulation closed some of the gap, but it never replaced the real test.

## Wall 8: the best validation loss was not the best policy

I loaded the checkpoint with the lowest validation loss (val_l1) onto the real arm. It trembled and did not reach the sponge. The lowest L1 loss did not make the best closed-loop policy.

I stopped relying on val_l1. I picked candidates between 10,000 and 25,000 steps that had a decent simulation success rate, ran each on the real robot, and narrowed them down by how smoothly they reached the target. In the scoring, best_model (the lowest val_l1) ranked 6th among all candidates.

## Wall 9: from 0/16 to 3/3

My first real evaluation failed 16 times in a row. The causes were tremor, short approaches, and a gripper that closed on nothing.

I re-ran the evaluation with the standardized layout and the selected layout39 checkpoints. On the L2 evaluation set, the arm completed grasp-and-place 3 out of 3 times, the first successful autonomous carry. With so few trials, the number is a reference value only. I changed several things between 0/16 and 3/3 and did not isolate which one mattered most.

## What I would tell someone starting the same project

- Do not teleoperate or record while preflight shows FAIL. Data collected with a shifted camera index or a wrong port is wasted.
- Turn off automatic phone camera handoff in the OS settings.
- Rest the servos about every 10 episodes to avoid tracking lag.
- Avoid nohup for recording, and use absolute paths.
- Do not move hardware to match old drawings or memory. Use the taped jig as the only reference.
- Dry-run before powering up, and keep the 12V plug within reach so you can cut power fast.
- Do not discard an episode only because it has a still period at the start or end. If it follows the protocol, it can help stabilize the policy.
- Do not pick checkpoints by val_l1 alone. Check behavior on the real robot or in a physics simulator too.

## Closing

On a small robot arm, standardizing the physical setup (power, ports, jig layout, heat) mattered about as much as choosing the model.

Everything is public. Clone the [repository](https://github.com/yohei1126/lerobot-so101-pick-and-place), read the bring-up steps in the [docs](https://yohei1126.github.io/lerobot-so101-pick-and-place/), try a dry-run on your desk, and watch the [demo video](https://youtu.be/hYQggz5CilA). The hardware is described in the [LeRobot SO-101 docs](https://huggingface.co/docs/lerobot/so101). The Japanese version is on [Zenn](https://zenn.dev/yohei/articles/2026-11-03-so101-sponge-paper-real-robot-walls).
