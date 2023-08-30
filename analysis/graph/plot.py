import plotly.graph_objects as go
import numpy as np
import pandas as pd

control_sample=np.load('C:/NONE/003_202308291643_complete.npy')
change_sample=np.load('C:/NONE/003_202308300837_both_1.npy')
third_sample=np.load('C:/NONE/003_202308300947.npy')
new_sample=np.load('C:/NONE/003_202308300827_black.npy')
a=np.load("C:/NONE/003_202308300957.npy")

fig = go.Figure([
    # go.Scatter(name='Control_Sample',
    #            x=control_sample[0],
    #            y=control_sample[1],
    #            mode='lines',
    #            line=dict(color='blue')
    #            ),
    # go.Scatter(name='both',
    #            x=change_sample[0],
    #            y=change_sample[1],
    #            mode='lines',
    #            line=dict(color='red'),
    #            ),

# go.Scatter(name='black',
#                x=new_sample[0],
#                y=new_sample[1],
#                mode='lines',
#                line=dict(color='green')
#                ),
go.Scatter(name='new_complete_Sample',
               x=third_sample[0],
               y=third_sample[1],
               mode='lines',
               line=dict(color='green')
               ),
go.Scatter(name='new_complete_Sample_2',
               x=a[0],
               y=a[1],
               mode='lines',
               line=dict(color='red')
               ),

])
fig.update_layout(
    yaxis_title='Reflection_Coefficient (dB)',
    xaxis_title='Distance (mm)',
    title='OFDR',
    hovermode='x'
)
fig.show()