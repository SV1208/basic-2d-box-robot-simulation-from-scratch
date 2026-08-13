installation:
Tested on python version 3.12.0 on windows system

activate the venv environment
> python -m venv venv
> venv/bin/Activate
> pip install -r requirements.txt

Install pysdl2 python bindings, and its compiled form
> pip install pysdl2 pysdl2-dll
https://pysdl2.readthedocs.io/en/0.9.13/tutorial/pong.html

Moving the robot in various direction using arrow keys
NOTE: -ve velocity mans going up in here
Left right is correct
(0,0)




            (4,4)
Coordinate System is like above.
Now just need to define heading properly and let it move

To test,
> python main.py
