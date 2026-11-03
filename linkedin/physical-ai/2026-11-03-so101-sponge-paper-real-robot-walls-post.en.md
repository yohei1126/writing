My first real-robot evaluation of an imitation-learning policy scored 0/16. A later policy completed grasp-and-place 3 out of 3 times on the L2 evaluation set. With n=3, that is a reference point, not a benchmark.

The model was not the main problem. The loop around it was: ports, power, camera indices, desk layout, servo heat, and how I picked checkpoints. Policy training was one of nine stages, and most of my lost time came from the other eight.

What I changed: a preflight script for serial ports and camera index (PASS/FAIL), a visual checklist for voltage, and a tape jig that fixed the arm base to sponge center at 140 mm and the arm base to paper center at 70 mm. I also cooled the arm about every 10 episodes, because tracking error rose from about 1.5° to 10-12° after roughly 20.

Two more findings. The checkpoint with the best validation loss ranked about sixth in my offline scoring on the real task, so I stopped choosing by val_l1 alone. And strong Temporal Ensembling (TE) smoothing contributed to the arm stalling before the target. I did not run an ablation, so I cannot say how much.

I changed several things between the 0/16 and the 3/3 and did not isolate which one mattered most.

Setup: SO-ARM101, LeRobot, ACT, trained on a Mac (MPS). I did this for Physical AI Applied 1 at the UTokyo Matsuo-Iwasawa Lab, and the course has finished.

Full write-up: [LINK TO ARTICLE]
Code: https://github.com/yohei1126/lerobot-so101-pick-and-place
Docs: https://yohei1126.github.io/lerobot-so101-pick-and-place/
Video: https://youtu.be/hYQggz5CilA

#Robotics #ImitationLearning #LeRobot #PhysicalAI
