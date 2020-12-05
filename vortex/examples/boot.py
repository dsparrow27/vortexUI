import os
from vortex import api as vortexApi
from vortex.examples import datamodel


def load():
    return vortexApi.standalone(None,
                                datamodel.Graph,
                                datamodel.Config,
                                filePath=os.path.join(os.environ["VORTEX"], "vortex/examples/example.vgrh"))


if __name__ == "__main__":
    load()
