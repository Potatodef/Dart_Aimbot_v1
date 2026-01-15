# Dart_Aimbot_v1
Using OpenCV to create a dart aimbot
The goal: 9 bullseye in a row
v1: Achieves the goal sometimes

## Requirement to pip install
pip install opencv-python numpy pyautogui pywin32

## Problems 
Optimising the code such that there is a higher rate of success can be done. However, achieving the goal 100% of the time is unlikely due to factors like lag which is not dependent on the software code. I think that although more sophisticated/ better written algorithms can be implemented, there is a trade-off between accuracy and speed, and since the lag factor is not constant, more accurate algos might take longer and be affected.

Additionally, screen size and different workstations might affect the size of the contours which might affect the detection of the dart. Template matching might have yielded a better result.

## Reflections
Initially, I approached the problem as a physics one relating to the projectile motion of a dart. Although it was partially correct, trying to calculate individual constants like acceleration and velocity led to inconsistent results. At this point, I was wondering whether the motion could even be related to newtonian physics, since the game might have used other methods like linear damping to produce a similar result. So I pivoted to mapping the coordinates of the dart and seeing whether it fit a shape in general. The results did show a parabolic shape, if so then it can be approximated that the motion follows kinematics, but what were the constants?

It turns out that by mapping the coordinates of the dart, it led to a true constant a in the equation ax^2 + bx +c =0. The kinematics equation relating Sx and Sy could reduce to this equation and b in this term related to tan(true_launch_angle). So to find the optimal launch angle for the next dart throw, I just needed to do a test dart throw to find a.

The reason why starting of with the kinematics equation didn't work was probably because due to lag, there is a difference between measured launch angle, determined by the dart tracking, and actual launch angle, which is determined by the equation. So to compensate for the difference, the first test dart is also used to find the difference between measured and actual.

## Assumptions
1.) The rotation angle of the dart, measured from tail to tip, is related to the launch angle of the dart.
In reality this might not be true.

2.) Actual angle is calculated close to dart starting point. So the actual angle can be approximated to the true actual starting angle.
If a lot of lag is involved, then this might be wrong.
