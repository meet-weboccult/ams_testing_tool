$ xhost +local:docker 
OR
$ xhost +local:root

$ docker run --rm -it -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=$DISPLAY -u qtuser testingapp python3 /tmp/main.py