# From 0/16 to a working SO-101 sponge place: the physical walls in imitation learning

My first real-robot evaluation of an imitation-learning policy scored 0/16. The model was not the main problem. The loop around it was: ports, power, camera indices, desk layout, servo heat, smoothing settings, and how I picked checkpoints.

After I fixed those, a later policy completed grasp-and-place 3 out of 3 times on the L2 evaluation set (verification set L2). With n=3, that is a reference point, not a benchmark. I did this work for Physical AI Applied 1 at the UTokyo Matsuo-Iwasawa Lab, and the course has finished.

## The task and the stack

The task was to pick a sponge with the gripper and place it on a sheet of paper.

- Robot: SO-ARM101 in a Leader/Follower setup ([LeRobot SO-101 docs](https://huggingface.co/docs/lerobot/so101))
- Framework and policy: LeRobot and ACT
- Cameras: a Logicool C920 as the top camera, and the follower gripper camera as the wrist camera
- Training: a Mac with MPS, about 25k steps, roughly 3.5 to 4 hours

The code is in [lerobot-so101-pick-and-place](https://github.com/yohei1126/lerobot-so101-pick-and-place). English docs are at [yohei1126.github.io/lerobot-so101-pick-and-place](https://yohei1126.github.io/lerobot-so101-pick-and-place/). A walkthrough video is on [YouTube](https://youtu.be/hYQggz5CilA).

## Training was one of nine stages, and most failures sat elsewhere

I split the project into nine stages:

1. Hardware wiring and power
2. Desk layout standardization
3. Preflight (ports + cameras) and framing checks
4. Teleoperation recording
5. Data QC
6. Policy training (Mac MPS / ACT)
7. Simulation evaluation
8. Checkpoint selection
9. Real-robot autonomous evaluation

Policy training was stage 6. Most of the time I lost came from the other eight.

## I confused 5V and 12V, and the board LED misled me

I mixed up the 5V and 12V supplies. The servo board LED could light up even when the 12V DC supply was not connected, so the LED gave me a false "powered" cue. I stopped trusting the LED and checked the supply itself.

## A preflight script caught port and camera mistakes, but not voltage

Wrong serial ports and shifted camera indices both produced runs that looked fine until the data was bad. The top and wrist camera indices were swapped between runs more than once. On a Mac, Continuity Camera can appear as an extra device and shift the camera indices.

I wrote a preflight script that checks fixed serial ports and the camera index, then prints PASS or FAIL. It did not check voltage, because the script could not see it. Voltage stayed on a visual checklist.

## A tape jig fixed the layout, and layout39 made episodes comparable

ACT depends on where objects sit in the image, so a layout change invalidates earlier data. I learned this the hard way: the physical layout changed three times before layout39, and each change invalidated the data I had already recorded for ACT.

I then fixed the geometry with a tape jig. The arm base to sponge center distance was 140 mm, and the arm base to paper center distance was 70 mm. Both objects were placed against tape marks.

I called the final standardized layout layout39. After I adopted it, episodes were comparable to each other.

## Servo heat degraded tracking, so I cooled the arm on a schedule

The servos heated up during recording. Tracking error rose from about 1.5° to 10-12° after about 20 episodes. Late episodes in a session were therefore noisier than early ones.

I cooled the arm about every 10 episodes. This was a manual rule, and it cost recording time.

## Simulation filtered obvious errors but gave false confidence

I used MuJoCo to check task logic before touching the robot. Two things misled me.

First, box-snap checks produced false positives. The simulator could report a placement as successful when the object had only snapped into the target volume.

Second, the success criteria differed from the real test. Simulation counted success within 25 mm and 15°. On the real robot, I judged placement visually. The two tests did not measure the same thing.

I used simulation only to catch obvious errors, and the visual placement check on the real robot was the final judge.

## Strong Temporal Ensembling made the real robot stall

TE here means Temporal Ensembling, the action-smoothing scheme used with ACT. On the real robot, strong TE smoothing contributed to the arm stalling before the target. It stopped short, as if stuck in glue. I did not run a controlled ablation, so I can say it contributed, not how much.

## A long training run wrote its output to the wrong place

Two process accidents cost me time. A training run started with nohup wrote its output somewhere I did not expect. Relative paths had resolved from the wrong working directory. After that, I used absolute paths and checked the working directory before starting any long run.

## The best validation loss was not the best policy

I had expected the checkpoint with the best val_l1 (saved as best_model) to perform best. In offline scoring on the real task, it ranked about sixth.

I switched to picking checkpoints by that offline score and stopped relying on val_l1 alone. The cost was extra scoring time before every real-robot trial.

## What the numbers do and do not show

With layout39, the heat rule, and offline checkpoint selection, a later policy completed grasp-and-place 3 out of 3 times on the L2 evaluation set. The first real evaluation had scored 0/16. I changed several things between those two results and did not isolate which one mattered most. Three trials cannot support a success rate.

## What I would tell someone starting the same project

- Automate the checks software can see (ports, camera indices) and keep a visual checklist for the rest (voltage).
- Do not trust a board LED as proof of power.
- Fix the physical layout before recording data you intend to keep. A tape jig is cheaper than recollecting episodes.
- Count episodes and cool the servos on a schedule.
- Use absolute paths and check the working directory before a long training run.
- Pick checkpoints by an offline score that resembles the real task, not by val_l1 alone.
- Treat simulation success as a necessary check, not as evidence that the robot will work.
- Be careful with strong TE smoothing on a real robot.

## Links

The repository contains the preflight check, the recording flow, and the evaluation setup. Start with the [English docs](https://yohei1126.github.io/lerobot-so101-pick-and-place/), clone the [repo](https://github.com/yohei1126/lerobot-so101-pick-and-place), or watch the [video](https://youtu.be/hYQggz5CilA). The SO-101 hardware is documented in the [LeRobot SO-101 docs](https://huggingface.co/docs/lerobot/so101). The Japanese write-up is on [Zenn](https://zenn.dev/yohei/articles/2026-11-03-so101-sponge-paper-real-robot-walls).
