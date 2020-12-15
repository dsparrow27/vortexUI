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

set PYTHONPATH=%PYTHONPATH%;%ABS_PATH%
set ZOO_PACKAGE_VERSION_PATH=%ABS_PATH%\zoo\package_version.config
set QT_SCALE_FACTOR=0.75
call %ZOOTOOLS_ROOT%\install\core\bin\zoo_cmd.bat env -- py "%ABS_PATH%\slithertest\slithermodel.py"
