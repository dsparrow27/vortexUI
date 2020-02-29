# vortexUI
PyQt node editor Widget

Very much still a WIP so not much is working right now.

##### Inital thoughts #####

VortexUI use's a high level objectModel approach to the node based problem,
instead of asking clients to deal directly with QtWidgets and knowing much of the internals.
we provide few high level objects to customize which should handle all aspects.

The Widget supports tabs, each tab consists of a new view and scene instance
but would be bound to a single global application instance sharing a root objectModel,
a ui config object and events.

Each objectModel instance would handle creating it's own attributes and handle
signally the ui for refresh.


###### Objects ######
Application
    High level scene object which has scene events and direct access to the config

ObjectModel
    Node level object

AttributeModel
    Attribute level object

##### Dependencies #####
zootoolspro
PySide2


#todo
1. create node from ui.
2. logging
3. uiPlugins no longer work
4. Node Attribute container doesn't expand with header text.
5. array element connections on expand/collapse need to reconnect to
   array.
6. Graph deserialization.






