import dash
from dash import dcc, html, dash_table, Input, Output, State
import plotly.graph_objects as go
import numpy as np

# Constants
ANGLE_INTENSITIES = {0: 1, 10: 0.95, 20: 0.85, 30: 0.73, 40: 0.6, 50: 0.45}
DISTANCES = np.arange(0, 10.5, 1)
ANGLES = list(ANGLE_INTENSITIES.keys())

app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("Received Power Density as a Function of Distance and Angle"),
    
    html.Div("Select LED type:"),
    dcc.Dropdown(
        id='led-type-dropdown',
        options=[
            {'label': 'Power LED', 'value': 'POWER'},
            {'label': 'TSAL6400', 'value': 'TSAL6400'},
            {'label': 'Custom', 'value': 'custom'}
        ],
        value='POWER',
        clearable=False
    ),
    
    html.Div(id='custom-intensities-input', children=[
        html.Div([html.Div(f"Angle {angle}:"), dcc.Input(id=f'angle-{angle}-input', type='number', value=1)]) for angle in ANGLES
    ], style={"display": "none"}),
    
    html.Br(),
    html.Div("Angle Intensities:", style={"margin-top": "20px"}),
    html.Div(id='angle-intensities-output', style={"width": "100%", "display": "inline-block", "vertical-align": "bottom", "margin-bottom": "20px"}),
    html.Br(),

    html.Div("LED Intensity (mw/sr):"),
    dcc.Input(id='led-intensity-input', value=5000, type='number'),
    html.Br(),
    html.Br(),
    html.Div("Number of LEDs:"),
    html.Br(),
    dcc.Slider(
        id='num-leds-slider',
        min=1,
        max=20,
        value=1,
        marks={i: str(i) for i in range(1, 21)},
        step=None,
        tooltip={"placement": "bottom", "always_visible": True},
        updatemode="drag"
    ),
    html.Br(),
    
    html.Div("Environment Factor:"),
    dcc.Input(id='environment-factor-input', value=22.22, type='number'),
    html.Br(),
    html.Br(),
    html.Div("Windshield Factor:"),
    dcc.Input(id='windshield-factor-input', value=4, type='number'),
    html.Br(),
    
    dcc.Graph(id='heatmap-output', style={"width": "100%", "display": "inline-block", "horizontal-align": "center", "vertical-align": "bottom", "margin-bottom": "20px"}),
    
    html.Div(id='table-output', style={"width": "100%", "display": "inline-block", "vertical-align": "bottom"})
])

@app.callback(
    Output('led-intensity-input', 'value'),
    [Input('led-type-dropdown', 'value')],
    [State('led-intensity-input', 'value')]
)
def set_default_intensity(led_type, current_intensity):
    if led_type == "POWER":
        return 2500
    elif led_type == "TSAL6400":
        return 420
    else:
        return current_intensity

@app.callback(
    [Output('heatmap-output', 'figure'),
     Output('table-output', 'children'),
     Output('angle-intensities-output', 'children')],
    [Input('num-leds-slider', 'value'),
     Input('led-intensity-input', 'value'),
     Input('environment-factor-input', 'value'),
     Input('windshield-factor-input', 'value'),
     Input('led-type-dropdown', 'value')] + 
     [Input(f'angle-{angle}-input', 'value') for angle in ANGLES]
)
def update_output(num_leds, led_intensity, env_factor, windshield_factor, led_type, *angle_values):
    
    # Calculate angle intensities locally rather than updating the global variable
    if led_type == "custom":
        angle_intensities = {angle: float(value or 0) for angle, value in zip(ANGLES, angle_values)}
    else:
        angle_intensities = ANGLE_INTENSITIES

    RADIANT_INTENSITY = num_leds * led_intensity
    
    env_factor = env_factor or 22.22
    windshield_factor = windshield_factor or 1

    def received_power_density(distance, angle):
        radiant_intensity_value = angle_intensities.get(angle, 0) or 0  # Use local angle_intensities
        radiant_intensity = RADIANT_INTENSITY * radiant_intensity_value
        return ((radiant_intensity / (distance**2 + 0.00001)) / env_factor) / windshield_factor

    HEATMAP_DISTANCES = np.arange(0, 10.2, 0.2)  # Up to 10 with steps of 0.2
    HEATMAP_DISTANCES_ADJUSTED = HEATMAP_DISTANCES + 0.00001

    Z_fine = np.array([[received_power_density(x, y) for x in HEATMAP_DISTANCES_ADJUSTED] for y in ANGLES])

    # Mask non-positive values
    Z_fine[Z_fine <= 0] = 1e-10

    # Now compute the log
    Z_log_fine = np.log10(Z_fine)
    hovertext_fine = np.array([[f"distance = {x:.2f}<br>angle = {y}<br>power density = {z:.2f}" for x, z in zip(HEATMAP_DISTANCES, row)] for y, row in zip(ANGLES, Z_fine)])

    heatmap_figure = go.Figure(go.Heatmap(
        z=Z_log_fine,
        x=HEATMAP_DISTANCES,
        y=ANGLES,
        colorscale='Viridis',
        hoverinfo="text",
        text=hovertext_fine,
        colorbar=dict(
            title="Received Power Density (mW/m^2)",
            tickvals=[np.log10(value) for value in [100, 1000, 10000, 100000, 1000000]],
            ticktext=["100", "1K", "10K", "100K", "1M"]
        )
    ))

    heatmap_figure.update_xaxes(side="top", range=[0, 10])
    heatmap_figure.update_yaxes(tickvals=ANGLES)
    heatmap_figure.update_layout(
        title="Received Power Density",
        autosize=False,
        width=1500,
        height=500,
        margin=dict(l=50, r=50, b=50, t=50),
        xaxis_title="Distance (m)",
        yaxis_title="Angle (degree)"
    )

    # Create the table
    table_header = [{'name': 'Angles \ Distances', 'id': 'Angle'}] + [{'name': str(d) + " m", 'id': str(d) + " m"} for d in DISTANCES]
    table_rows = [{'Angle': angle, **{str(d) + " m": received_power_density(d, angle) for d in DISTANCES}} for angle in ANGLES]
    table = dash_table.DataTable(
        id='table',
        columns=table_header,
        data=table_rows,
        style_table={'height': '300px', 'overflowY': 'auto'},
        style_cell={'textAlign': 'center', 'width': '80px', 'minWidth': '80px', 'maxWidth': '80px'},
        style_header={
            'backgroundColor': 'rgb(30, 30, 30)',
            'color': 'white'
        }
    )

    angle_table_data = [{"Angular Displacement": angle, "Relative Radiant Intensity": angle_intensities[angle]} for angle in ANGLES]
    angle_table_columns = [{"name": "Angular Displacement", "id": "Angular Displacement"},
                        {"name": "Relative Radiant Intensity", "id": "Relative Radiant Intensity"}]
    angle_intensities_table = dash_table.DataTable(data=angle_table_data, columns=angle_table_columns,
                                                   style_table={'height': '200px', 'overflowY': 'auto'},
                                                   style_cell={'textAlign': 'center'})

    return heatmap_figure, table, angle_intensities_table

@app.callback(
    Output('custom-intensities-input', 'style'),
    [Input('led-type-dropdown', 'value')]
)
def show_hide_custom_inputs(led_type):
    if led_type == "custom":
        return {"display": "block"}
    else:
        return {"display": "none"}

if __name__ == '__main__':
    app.run_server(debug=True)
