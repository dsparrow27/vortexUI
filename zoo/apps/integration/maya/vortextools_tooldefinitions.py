from zoo.apps.toolpalette import palette
from slithertest import slithermodel
from vortex import api


class VortexUI(palette.ToolDefinition):
    id = "zoo.vortex.ui"
    creator = "David Sparrow"
    tags = ["vortex"]
    uiData = {"icon": "cubeArray",
              "tooltip": "Opens the vortex UI",
              "label": "Vortex UI",
              "color": "",
              "backgroundColor": "",
              "multipleTools": False,
              }

    def execute(self, *args, **kwargs):
        win = api.maya(slithermodel.Application,
                       slithermodel.Graph,
                       slithermodel.Config)
        print(win)
        return win
