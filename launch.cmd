
@echo off

rem // Save value of CD variable (current directory)
set ABS_PATH=%CD%
call %ABS_PATH%/env.cmd
echo %VORTEX%
echo %VORTEX%/env.cmd
py "./vortex/examples/boot.py"