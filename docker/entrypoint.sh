#!/usr/bin/env sh
set -eu

mkdir -p /tmp/.X11-unix

Xvfb :1 -screen 0 1600x900x24 &
fluxbox > /tmp/fluxbox.log 2>&1 &

# noVNC static client + websocket proxy.
websockify --web=/usr/share/novnc/ ${NOVNC_PORT:-6080} localhost:${VNC_PORT:-5901} > /tmp/websockify.log 2>&1 &

x11vnc -display :1 -forever -shared -nopw -rfbport ${VNC_PORT:-5901} > /tmp/x11vnc.log 2>&1 &

exec python src/app.py