import os, sys

zooRoot = os.environ["ZOOTOOLS_ROOT"]
scriptpath = os.path.join(zooRoot, "install", "core", "scripts")
sys.path.append(scriptpath)

import zoo_cmd
zoo_cmd.install(scriptpath, ("env", ))
sys.path.append(os.path.join(os.environ["VORTEX"], "slithertest"))

import slithermodel
slithermodel.load()
