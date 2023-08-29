import plotly.graph_objects as go
import numpy as np
import pandas as pd

control_sample=np.load('C:/NONE/003_202308291643.npy')
change_sample=np.load('C:/NONE/003_202308291648.npy')
third_sample=np.load('C:/NONE/003_202308291651.npy')
no_sample=np.load('C:/NONE/003_202308291708.npy')

fig = go.Figure([
    go.Scatter(name='Control_Sample',
               x=control_sample[0],
               y=control_sample[1],
               mode='lines',
               line=dict(color='blue')
               ),
 #    go.Scatter(name='New_Sample',
 #               x=change_sample[0],
 #               y=change_sample[1],
 #               mode='lines',
 #               line=dict(color='red'),
 #               ),
 # go.Scatter(name='3rd_Sample',
 #               x=third_sample[0],
 #               y=third_sample[1],
 #               mode='lines',
 #               line=dict(color='green')
 #               ),
go.Scatter(name='No_Sample',
               x=no_sample[0],
               y=no_sample[1],
               mode='lines',
               line=dict(color='green')
               )
])
fig.update_layout(
    yaxis_title='Reflection_Coefficient (dB)',
    xaxis_title='Distance (mm)',
    title='OFDR',
    hovermode='x'
)
fig.show()