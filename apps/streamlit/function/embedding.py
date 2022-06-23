import fiftyone as fo
import fiftyone.brain as fob
import dash
import plotly.express as px
import plotly.graph_objects as go
import math
import pandas as pd

import random

def compute_embeddings(dataset):
    return fob.compute_visualization(
        dataset,
        num_dims=2,
        brain_key="image_embeddings",
        verbose=True,
        seed=51,
        patches_field="ground_truth"
    ).points

def create_dataframe(dataset):
    embeddings = compute_embeddings(dataset)
    
    df = pd.DataFrame(columns=['index', 'uniqueness', 'label','sqrt_area','embeddings_x', 'embeddings_y'])
    
    index = 0
    for sample in dataset:
        for detection in sample.ground_truth.detections:
            df.loc[index] = [index, sample.uniqueness, detection.label, math.sqrt(detection.area), embeddings[index,0], embeddings[index, 1]]
            df.loc[index] = [index, sample.uniqueness, detection.label, math.sqrt(detection.area), random.random(), random.random()]
            index += 1
    
    return df

class Dataset:

    def create_partial_dataset(self):
        self.partial_dataset = fo.Dataset()
        self.update_partial_dataset([i for i in range(self.num_detection)])

    def get_sample_indices(self, indices):
        sample_indices = set()
        for index in indices:
            detection_id = self.connection_index_detection[index]
            sample_id = self.connection_detection_sample[detection_id]
            sample_indices.add(sample_id)
        return sample_indices

    def update_partial_dataset(self, indices):
        sample_indices = self.get_sample_indices(indices)
        
        self.partial_dataset.clear()
        self.connection_sample_partial = dict()
        self.connection_partial_sample = dict()

        for sample_id in sample_indices:
            sample = self.dataset[sample_id]
            partial_id = self.partial_dataset.add_sample(sample)
            self.connection_sample_partial[sample_id] = partial_id
            self.connection_partial_sample[partial_id] = sample_id

        print('Updated partial dataset.')

    def overwrite_partial_sample(self, partial_id, sample_id):
        partial = self.partial_dataset[partial_id]
        sample = self.dataset[sample_id]
        
        sample_detection_ids = [sample_detection.id for sample_detection in sample.ground_truth.detections]
        indices = [self.connection_detection_index[sample_detection_id] for sample_detection_id in sample_detection_ids]

        assert len(sample_detection_ids) == len(set(sample_detection_ids)), f"{sample} {sample_detection_ids}"

        for sample_detection_id in sample_detection_ids:
            del self.connection_detection_index[sample_detection_id]
        
        del self.connection_sample_detection[sample_id]
        for sample_detection_id in sample_detection_ids:
            del self.connection_detection_sample[sample_detection_id]
        
        self.dataset.delete_samples(sample_id)
        sample_id = self.dataset.add_sample(partial)
        sample = self.dataset[sample_id]

        sample_detection_ids = [sample_detection.id for sample_detection in sample.ground_truth.detections]

        for index, sample_detection_id in zip(indices, sample_detection_ids):
            self.connection_detection_index[sample_detection_id] = index
            self.connection_index_detection[index] = sample_detection_id
        
        for pos, sample_detection_id in enumerate(sample_detection_ids):
            if not pos: self.connection_sample_detection[sample_id] = set()
            self.connection_sample_detection[sample_id].add(sample_detection_id)
            self.connection_detection_sample[sample_detection_id] = sample_id
        
    def sync(self):
        for partial in self.partial_dataset:
            partial_id = partial.id            
            sample_id = self.connection_partial_sample[partial_id]
            self.overwrite_partial_sample(partial_id, sample_id)

        print('Synced dataset.')

    def create_connection(self):
        self.connection_index_detection = dict()
        self.connection_detection_index = dict()

        self.connection_detection_sample = dict()
        self.connection_sample_detection = dict()

        self.connection_sample_partial = dict()
        self.connection_partial_sample = dict()

        index = 0
        for sample in self.dataset:
            for pos, detection in enumerate(sample.ground_truth.detections):
                self.connection_index_detection[index] = detection.id
                self.connection_detection_index[detection.id] = index

                if not pos: self.connection_sample_detection[sample.id] = set()
                self.connection_sample_detection[sample.id].add(detection.id)
                self.connection_detection_sample[detection.id] = sample.id

                index += 1
        
        self.num_detection = index

    def __init__(self, dataset):
        self.dataset = dataset
        self.create_connection()
        self.create_partial_dataset()

def create_app(dataset):
    
    def create_figure(df, min_uniqueness, max_uniqueness, min_sqrt_area, max_sqrt_area):
        mask = (df['uniqueness'] >= min_uniqueness) & (df['uniqueness'] <= max_uniqueness) & (df['sqrt_area'] >= min_sqrt_area) & (df['sqrt_area'] <= max_sqrt_area)
        fig = px.scatter(df[mask], x='embeddings_x', y='embeddings_y', color='label', size='sqrt_area', custom_data=['index'], hover_data=['uniqueness'])
        figure = go.FigureWidget(fig)
        figure.update_layout(
            autosize=True,
            width=1080,
            height=566,
        )
        return figure
    
    df = create_dataframe(dataset)

    global_uniqueness_range = (0, 1)
    global_sqrt_area_range = (0, df['sqrt_area'].max())
    
    figure = create_figure(df, global_uniqueness_range[0], global_uniqueness_range[1], global_sqrt_area_range[0], global_sqrt_area_range[1])

    app = dash.Dash(__name__)
    app.layout = dash.html.Div(children=[
        dash.html.H3('Embedding Visualization'),
        dash.dcc.Graph(
            id='graph',
            figure=figure
        ),
        dash.html.P(id='num_sample'),
        dash.html.P('Filter by uniqueness:'),
        dash.dcc.RangeSlider(
            id='uniqueness-slider',
            min=0, max=1, step=0.001,
            marks={0: '0', 1: '1'},
            value=[0, 1]
        ),
        dash.html.P('Filter by sqrt area:'),
        dash.dcc.RangeSlider(
            id='sqrt-area-slider',
            min=0, max=df['sqrt_area'].max(), step=df['sqrt_area'].max()/1000,
            marks={0: '0', df['sqrt_area'].max(): f'{df["sqrt_area"].max()}'},
            value=[0, df['sqrt_area'].max()]
        ),
    ])

    @app.callback(
        dash.Output('graph', 'figure'), 
        dash.Input('uniqueness-slider', 'value'),
        dash.Input('sqrt-area-slider', 'value'),
    )
    def update_figure(uniqueness_slider_range, sqrt_area_slider_range):
        global_uniqueness_range = uniqueness_slider_range
        global_sqrt_area_range = sqrt_area_slider_range
        figure = create_figure(df, global_uniqueness_range[0], global_uniqueness_range[1], global_sqrt_area_range[0], global_sqrt_area_range[1])
        print(f'Updated uniquesness range to {global_uniqueness_range}')
        print(f'Updated sqrt area range to {global_sqrt_area_range}')
        return figure
    
    return app

def main(dataset, dash_port, session_port, key):
    app = create_app(dataset)
    dataset = Dataset(dataset)

    @app.callback(
        dash.Output(component_id='num_sample', component_property='children'),
        dash.Input(component_id='graph', component_property='selectedData')
    )
    def update(input_value):
        if input_value is not None:
            indices = [point['customdata'][0] for point in input_value['points']]
            dataset.sync()
            dataset.update_partial_dataset(indices)
        return f'Number of sample: {len(dataset.partial_dataset)}'
    
    session = fo.launch_app(dataset.partial_dataset, address='0.0.0.0', port=session_port, remote=True)
    app.run_server(debug=False, host='0.0.0.0', port=dash_port)