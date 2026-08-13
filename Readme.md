installation:
activate the venv environment
> venv/bin/Activate

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
