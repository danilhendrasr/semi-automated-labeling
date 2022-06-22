import fiftyone as fo
import fiftyone.brain as fob
import dash
from plotly.graph_objs import FigureWidget

def compute_embeddings(dataset):
    return fob.compute_visualization(
        dataset,
        num_dims=2,
        brain_key="image_embeddings",
        verbose=True,
        seed=51,
        patches_field="ground_truth"
    ).points

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

class Graph:
    def create_app(self):
        self.app = dash.Dash(__name__)
        self.app.layout = dash.html.Div(children=[
            dash.dcc.Graph(
                id=self.key['graph'],
                figure=self.figure
            ),
            dash.html.Div(
                id=self.key['output']
            )
        ])

    def create_figure(self, embeddings):
        self.trace = dict(
            type='scatter',
            x=embeddings[:, 0],
            y=embeddings[:, 1],
            mode='markers'
        )

        self.layout = dict(
            width=600, 
            height=550, 
            autosize=False,
            xaxis=dict(zeroline=False),
            dragmode='lasso',
            hovermode='closest'
        )

        self.figure = FigureWidget(data=[self.trace], layout=self.layout)
    
    def create_key(self, key=None):
        if key is None: key = hash(self)
        self.key = dict()
        self.key['graph'] = f'{key} key'
        self.key['output'] = f'{key} output'

    def __init__(self, embeddings):
        self.create_key()
        self.create_figure(embeddings)
        self.create_app()
    
    def get_app(self):
        return self.app

def main(dataset, dash_port, session_port, key):
    embeddings = compute_embeddings(dataset)
    dataset = Dataset(dataset)
    graph = Graph(embeddings)
    app = graph.get_app()

    @app.callback(
        dash.Output(component_id=graph.key['output'], component_property='children'),
        dash.Input(component_id=graph.key['graph'], component_property='selectedData')
    )
    def update(input_value):
        if input_value is not None:
            indices = [point['pointIndex'] for point in input_value['points']]
            dataset.sync()
            dataset.update_partial_dataset(indices)
        return f'Number of sample: {len(dataset.partial_dataset)}'
    
    session = fo.launch_app(dataset.partial_dataset, address='0.0.0.0', port=session_port, remote=True)
    app.run_server(debug=False, host='0.0.0.0', port=dash_port)

    dataset.sync()
    dataset = dataset.dataset
    return dataset