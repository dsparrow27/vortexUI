

set VORTEX=D:\code\python\personal\vortexUI
set PYTHONPATH=%PYTHONPATH%;%VORTEX%
set ZOO_PACKAGE_VERSION_PATH=%VORTEX%\zoo\package_version.config
echo %ZOOTOOLS_PRO_ROOT%
call %ZOOTOOLS_PRO_ROOT%\install\core\bin\zoo_cmd.bat env -- py "%VORTEX%\vortex\examples\boot.py"