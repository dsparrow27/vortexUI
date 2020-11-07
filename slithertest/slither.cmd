@echo off
setlocal
set REL_PATH=..\
set ABS_PATH=

rem // Save current directory and change to target directory
pushd %REL_PATH%

rem // Save value of CD variable (current directory)
set ABS_PATH=%CD%

rem // Restore original directory
popd

call %ABS_PATH%/env.cmd
set SLITHER=F:\code\python\personal\slither
set SLITHER_PLUGIN_PATH=%SLITHER%\slither\plugins
echo %SLITHER_PLUGIN_PATH%
set PYTHONPATH=%PYTHONPATH%;%SLITHER%;%ZOOTOOLS_ROOT%\install\core\python
call py "%VORTEX%\slithertest\slithermodel.py"
