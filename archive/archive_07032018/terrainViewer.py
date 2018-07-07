import Earthly as ea # import my awesome library

SouthTable = ea.Region('NTable') # create a region object
SouthTable.add_CoordLayer(5) # add 2D coordinate layer data member
SouthTable.add_ElevLayer() # add 2D elevation layer data member
SouthTable.ElevVis() # generate visualization library using plotly
