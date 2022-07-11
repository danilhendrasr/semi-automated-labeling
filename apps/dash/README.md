# fiftyone-plotly-dash

This repository integrates [fiftyone image embeddings](https://voxel51.com/docs/fiftyone/tutorials/image_embeddings.html) to web browser using [plotly-dash](https://plotly.com/dash/), so that user no longer need to use jupyter notebook or jupyter lab to preview and interact with image embeddings plot.

<img src="resources/demo.gif"/>

## Usage

The program `app_flask.py` responsible to serve fiftyone application, while the program `app_dash.py` responsible to serve plotly plot on dash server. Both programs need to be run parallely in order to work as it should.

Run the following command on terminal to clone this repository, then execute `run.sh` to run `app_flask.py` and `app_dash.py` in parallel.

```
git clone https://github.com/Xu-Justin/fiftyone-plotly-dash.git
cd fiftyone-plotly-dash
./run.sh
```

## API

| Method | Route                      | Request                               | Description                                                                                                                                           |
|:------:|----------------------------|---------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| `GET`  | `/fiftyone/<name>`         | -                                     | Redirect to fiftyone tab wtih `<name>` dataset.                                                                                                       |
| `GET`  | `/embedding/<name>`        | -                                     | Redirect to plotly dash tab with `name` embeddings.                                                                                                   |
| `POST` | `/compute`                 | <pre>'name': str</pre>                | Compute `name` dataset uniqueness and embeddings. Then saved `name` dataset information, uniqueness, and embeddings to `name.pickle` at cache folder. |
| `POST` | `/fiftyone/update`         | <pre>'name': str<br>'ids': list</pre> | Update current fiftyone session to `name` dataset and view to selected patches `ids`.                                                                 |
| `POST` | `/fiftyone/save/view`      | -                                     | Save fiftyone session view.                                                                                                                           |
| `POST` | `/delete/cache`            | -                                     | Delete cache folder files.                                                                                                                            |
| `POST` | `/fiftyone/delete/dataset` | -                                     | Delete all fiftyone dataset on the database.                                                                                                          |
| `POST` | `/fiftyone/load/from_dir`  | <pre>'name': str<br>'dir': str</pre>  | Load fiftyone dataset from `dir` and saved as `name` dataset.                                                                                         |

## Docker

It is recommended to do the inference inside a docker container to prevent version conflicts. The container image for this project is available on  [Docker Hub](https://hub.docker.com/repository/docker/jstnxu/fiftyone-plotly-dash) and can be pulled using the following commands.

```
docker pull jstnxu/fiftyone-plotly-dash
```

The following commands will run the docker image.
  
```
docker run -it --ipc=host -v <local_fiftyone>:/root/.fiftyone/ -p <local_port>:6000-6003 --rm jstnxu/fiftyone-plotly-dash
```

---
  
This project was developed as part of Nodeflux Internship x Kampus Merdeka.
