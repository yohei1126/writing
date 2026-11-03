# From 0/16 to a working sponge place on a desktop robot arm

My first live evaluation of an imitation-learning policy on a real robot arm scored 0/16. A later policy completed grasp-and-place 3 out of 3 times on the L2 evaluation set. With n=3, that is a reference point, not a benchmark.

The model was not the main problem. The loop around it was: power, ports, camera indices, desk layout, servo heat, simulation criteria, and how I chose checkpoints. Policy training was one of nine stages, and most of the problems came from the other eight.

What I changed:

- A preflight script that checks fixed serial ports and camera indices (PASS/FAIL), plus a visual checklist for the 12V supply.
- A masking-tape jig: arm base to sponge center 140 mm, arm base to paper center 70 mm (layout39).
- A rest about every 10 episodes, because shoulder_lift tracking lag grew from about 1.5° to 10-12° after roughly 20.
- Checkpoints chosen by real-robot behavior. The lowest val_l1 checkpoint (best_model) ranked 6th among the candidates.
- Tuned Temporal Ensembling (TE). Strong smoothing made the real arm stall short of the target.

I changed several things between the 0/16 and the 3/3 and did not isolate which one mattered most.

Setup: SO-ARM101, LeRobot, ACT, MuJoCo, trained on a MacBook Pro (MPS). This was my final assignment for Physical AI Applied 1 at the UTokyo Matsuo-Iwasawa Lab, and the course has finished.

Full write-up: [LINK TO ARTICLE]
Code: https://github.com/yohei1126/lerobot-so101-pick-and-place
Docs: https://yohei1126.github.io/lerobot-so101-pick-and-place/
Video: https://youtu.be/hYQggz5CilA

#Robotics #ImitationLearning #LeRobot #PhysicalAI
