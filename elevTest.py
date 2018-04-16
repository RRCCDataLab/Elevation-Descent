import Earthly as ea

SouthTable = ea.Region('SouthTable')
SouthTable.add_CoordLayer(5)
SouthTable.add_ElevLayer()
SouthTable.ElevVis()
