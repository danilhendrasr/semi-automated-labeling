import fiftyone as fo
import fiftyone.brain as fob
import dash
from plotly.graph_objs import FigureWidget

def compute(dataset):
    return fob.compute_visualization(
        dataset,
        num_dims=2,
        brain_key="image_embeddings",
        verbose=True,
        seed=51,
    ).points

def create_FigureWidget(embeddings):
    trace = dict(
        type='scatter',
        x=embeddings[:, 0],
        y=embeddings[:, 1],
        mode='markers'
    )

    layout = dict(
        width=600, 
        height=550, 
        autosize=False,
        xaxis=dict(zeroline=False),
        dragmode='lasso',
        hovermode='closest'
    )

    return FigureWidget(data=[trace], layout=layout)

def main(dataset, dash_port, session_port, function_key):
    
    index2id = dict()
    id2index = dict()
    for i, sample in enumerate(dataset):
        index2id[i] = sample.id
        id2index[sample.id] = i
    
    embeddings = compute(dataset)
    figure = create_FigureWidget(embeddings)
    
    dash_dataset = fo.Dataset()
    for sample in dataset:
        dash_dataset.add_sample(sample)

    app = dash.Dash(__name__)
    app.layout = dash.html.Div(children=[
        dash.dcc.Graph(
            id=f'{function_key} dash-graph',
            figure=figure
        ),
        dash.html.Div(id=f'{function_key} my-output')
    ])

    @app.callback(
        dash.Output(component_id=f'{function_key} my-output', component_property='children'),
        dash.Input(component_id=f'{function_key} dash-graph', component_property='selectedData')
    )
    def update(input_value):
        if input_value is not None:
            dash_dataset.clear()
            for point in input_value['points']:
                index = point['pointIndex']
                dash_dataset.add_sample(dataset[index2id[index]])
        return f'Number of sample: {dash_dataset}'
    
    session = fo.launch_app(dash_dataset, address='0.0.0.0', port=session_port)
    app.run_server(debug=False, host='0.0.0.0', port=dash_port)

if __name__ == '__main__':
    import fiftyone.zoo as foz
    dataset = foz.load_zoo_dataset("quickstart")
    main(dataset, dash_port=5201, session_port=5202, function_key=__name__)