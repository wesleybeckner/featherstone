<small>created by [wesley beckner](http://wesleybeckner.github.io)</small>

# Asset Capability Dashboard

This is an [asset capability dashboard](https://belpre.herokuapp.com) demo using [Dash](https://plot.ly/products/dash/)

## Getting Started

### Running the app locally

First create a virtual environment with conda (or venv) and activate it.

```

conda create -n <your_env_name> python==3.7
source activate <your_env_name>

```

Clone the git repo, then install the requirements with pip

```

git clone https://github.com/wesleybeckner/featherstone.git
cd featherstone
pip install -r requirements.txt

```

Run the app

```

python app.py

```

## About the app

This is an interactive app to assess asset capability for manufacturing plants.

There is hidden capability within plant assets due to variability in uptime, yield, and rate. By assessing these variabilities with regard to unique products and operators, the hidden capabilities can be evaluated and monetized for each asset. Setting the "Performance Quantile" re-centers these performance distributions to the selected quantile and computes the resulting production opportunity. Operator/product/downtime events that poorly impact performance can be investigated within the dashboard.


## Built With

- [Dash](https://dash.plot.ly/) - Main server and interactive components
- [Plotly Python](https://plot.ly/python/) - Used to create the interactive plots
