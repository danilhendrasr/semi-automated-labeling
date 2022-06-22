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
    ).points

class Dataset:
    def create_partial_dataset(self):
        self.partial_dataset = fo.Dataset()
        for sample in self.dataset:
            id = self.partial_dataset.add_sample(sample)
            self.connection_partial_dataset[id] = sample.id
            self.connection_dataset_partial[sample.id] = id
        print('Created new partial dataset.')

    def update_partial_dataset(self, indices=None):
        self.partial_dataset.clear()
        self.connection_partial_dataset = dict()
        self.connection_dataset_partial = dict()
        if indices is None:
            for sample in self.dataset:
                id = self.partial_dataset.add_sample(sample)
                self.connection_partial_dataset[id] = sample.id
                self.connection_dataset_partial[sample.id] = id
        else:
            for index in indices:
                dataset_id = self.connection_index_dataset[index]
                sample = self.dataset[dataset_id]
                id = self.partial_dataset.add_sample(sample)
                self.connection_partial_dataset[id] = sample.id
                self.connection_dataset_partial[sample.id] = id
        print('Updated partial dataset.')

    def sync(self):
        for sample in self.partial_dataset:
            partial_id = sample.id
            dataset_id = self.connection_partial_dataset[partial_id]
            index_id = self.connection_dataset_index[dataset_id]

            self.dataset.delete_samples(dataset_id)
            del self.connection_partial_dataset[partial_id]
            del self.connection_dataset_partial[dataset_id]
            del self.connection_index_dataset[index_id]
            del self.connection_dataset_index[dataset_id]
            
            dataset_id = self.dataset.add_sample(sample)
            self.connection_partial_dataset[partial_id] = dataset_id
            self.connection_dataset_partial[dataset_id] = partial_id
            self.connection_index_dataset[index_id] = dataset_id
            self.connection_dataset_index[dataset_id] = index_id

        print('Synced dataset.')

    def create_connection(self):
        self.connection_index_dataset = dict()
        self.connection_dataset_index = dict()
        self.connection_dataset_partial = dict()
        self.connection_partial_dataset = dict()

        for i, sample in enumerate(self.dataset):
            self.connection_index_dataset[i] = sample.id
            self.connection_dataset_index[sample.id] = i

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

def main(dataset, dash_port, session_port):
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

if __name__ == '__main__':
    import fiftyone.zoo as foz
    dataset = foz.load_zoo_dataset("quickstart")
    main(dataset, dash_port=5201, session_port=5202)