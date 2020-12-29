##AestheticFeatureExtractorApi


AestheticFeatureExtractorApi is a python tool which offers the following functionalities:

1. Communicates with the aesthetic signature predictors, as specified in the *config_files/input_config.json*.
2. Sends all images to said predictors and stores the corresponding predictions in the *config_files/prediction_results.json*.

###Requirements

This project requires Python 3.
    
###Installation

Clone this repository and install the project requirements:

```bash
pip install -r requirements.txt
```

###Usage

As this project depends on the Aesthetic Predictors defined in the *config_files/input_config.json*, it is not intended for an isolated usage.
Recommended usage is by cloning this [repository](https://github.com/RibinMTC/DockerConfigShare) and running docker-compose in it.

For running the code locally, run the following command from the project's root directory:

```bash
python3 ./src/aesthetic_feature_extractor_api_main.py
```

