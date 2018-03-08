import numpy as np
import pandas as pd
import plotly.offline as offline
import plotly.plotly as py
import plotly.graph_objs as go

elevDataCube = np.load('RRCC_Gulch.npy')

elevDataMatrix = np.transpose(np.transpose(elevDataCube)[2][:])

elevDF = pd.DataFrame(data=elevDataMatrix)



# Read data from a csv
z_data = elevDF

data = [
    go.Surface(
        z=z_data.as_matrix()
    )
]
layout = go.Layout(
    title='RRCC Gulch',
    autosize=False,
    width=500,
    height=500,
    margin=dict(
        l=65,
        r=50,
        b=65,
        t=90
    )
)
fig = go.Figure(data=data, layout=layout)
offline.plot(fig, filename='RRCC_Gulch-3d-surface')
