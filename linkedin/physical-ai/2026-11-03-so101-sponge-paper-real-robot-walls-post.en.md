My first real-robot evaluation scored 0/16. The SO-101 arm trembled, stopped short, or missed the grasp.

The model was not the main cause. The physical loop was: mixed-up ports, a 5V/12V power confusion, swapped camera indices, a layout I changed three times, and servos that drifted from about 1.5° to 10–12° error after roughly 20 episodes.

What helped was unglamorous. A preflight check for ports and camera index (PASS/FAIL), a visual checklist for voltage, a tape jig for the sponge and paper, and cooling the arm about every 10 episodes.

One more surprise: the checkpoint with the best validation loss ranked about sixth in my offline scoring on real-task criteria. Choosing checkpoints differently mattered.

After those changes, the policy completed grasp-and-place 3 out of 3 times. That is a small sample, so read it as a reference, not a benchmark.

Setup: SO-ARM101, LeRobot, ACT, trained on a Mac (MPS). Done for Physical AI Applied 1 at UTokyo Matsuo–Iwasawa Lab.

Full write-up: [LINK TO ARTICLE]
Code and EN docs: https://github.com/yohei1126/lerobot-so101-pick-and-place
Docs: https://yohei1126.github.io/lerobot-so101-pick-and-place/
Video (currently Japanese): https://youtu.be/hYQggz5CilA

#Robotics #ImitationLearning #LeRobot #PhysicalAI
