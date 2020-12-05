for %%i in ("%~dp0.") do SET "VORTEX=%%~fi"
@echo off

set ZOO_PACKAGE_VERSION_PATH=%VORTEX%\zoo\package_version.config
call %ZOOTOOLS_ROOT%\install\core\bin\zoo_cmd.bat env -- py "%VORTEX%/vortex/examples/boot.py"