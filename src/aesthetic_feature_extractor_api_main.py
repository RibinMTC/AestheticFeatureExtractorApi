"""
Main module which communicates with the aesthetic signature predictors
Responsibilities:
    1.  Poll each aesthetic predictor specified in the config_files/input_config.json until they are ready
        to start prediction.
    2.  Send all images to the predictors and store predicted values to an output json file (prediction_results.json).
"""
import json
import os
import shutil
import time
from pathlib import Path
import requests


def get_dict_from_json(json_path):
    with json_path.open() as json_file:
        json_dict = json.load(json_file)
        return json_dict


def write_dict_to_json(json_path, dict_to_write):
    with json_path.open('w') as json_file:
        json.dump(dict_to_write, json_file, indent=4)


def create_dir(dir_path):
    os.mkdir(dir_path)


def copy_user_content_to_server_folder(user_content_folder_path, server_import_folder_path):
    for content in user_content_folder_path.iterdir():
        shutil.copy(content, server_import_folder_path.absolute())
    print("Copied Files to Server")


def delete_content_from_server_folder(server_import_folder_path):
    shutil.rmtree(server_import_folder_path.absolute())
    print("Removed Files from Server")


def send_post_request_and_receive_response(dict_to_send, predictor_address):
    try:
        response = requests.post(predictor_address, json=dict_to_send)
        return response.json()
    except Exception as e:
        print(str(e))
        return None


def send_get_request_and_receive_response(predictor_address):
    try:
        response = requests.get(predictor_address)
        if "Model not initialized" in str(response.content):
            return None
        return "Model initialized"
    except Exception as e:
        print(str(e))
        return None


def start_prediction(img_folder_path, selected_predictors, predictors_address):
    print("Starting prediction...")
    if not all(selected_predictor in predictors_address.keys() for selected_predictor in selected_predictors):
        print("Selected predictor names are invalid. Please make sure that the predictor name is between 1 and 4")
        print("Aborting prediction")
        return

    image_predictions_dict = {}
    for img_path in os.listdir(img_folder_path):
        if not (img_path.endswith(".png") or img_path.endswith(".jpg")):
            print("Image format not supported for: " + str(img_path) + "Skipping prediction for this image")
            continue
        predictions_dict = {}
        abs_img_path = os.path.join(img_folder_path, img_path)
        for selected_predictor_key in selected_predictors:
            dict_to_send = {'contentPath': abs_img_path, 'startFrame': 0, 'endFrame': 0}
            predictor_response_dict = send_post_request_and_receive_response(dict_to_send,
                                                                             predictors_address[selected_predictor_key])
            if predictor_response_dict is None:
                continue
            predictions_dict[selected_predictor_key] = predictor_response_dict
        image_predictions_dict[img_path] = predictions_dict

    print("Prediction finished")
    return image_predictions_dict


def poll_predictors_until_ready(selected_predictors, predictors_address):
    for selected_predictor_key in selected_predictors:
        print("Waiting for connection with: " + selected_predictor_key + " ...")
        while True:
            predictor_response = send_get_request_and_receive_response(predictors_address[selected_predictor_key])
            if predictor_response is None:
                time.sleep(5)
            else:
                print("Connection established to predictor: " + selected_predictor_key)
                break


_base_path = Path(__file__).parent.parent
_config_files_path = _base_path / 'config_files'
_predictors_address_path = _config_files_path / 'predictors_address.json'
_deploy_predictors_address_path = _config_files_path / 'predictors_address_deploy.json'
_input_config_path = _config_files_path / 'input_config.json'
_output_json_file = _config_files_path / 'prediction_results.json'

_input_config = get_dict_from_json(_input_config_path)
_selected_predictors = _input_config['predictors']
_deploy = _input_config['deploy']

if _deploy:
    _predictors_address = get_dict_from_json(_deploy_predictors_address_path)
    _server_content_folder_path = Path('/content_storage/prediction_images')
else:
    _predictors_address = get_dict_from_json(_predictors_address_path)
    _server_content_folder_path = _base_path / 'content_storage_test/prediction_images'

_initialized_poll_address = {k: v + '/is_model_ready' for k, v in _predictors_address.items()}
_predictors_address = {k: v + '/predict' for k, v in _predictors_address.items()}

poll_predictors_until_ready(_selected_predictors, _initialized_poll_address)
_image_predictions_dict = start_prediction(_server_content_folder_path, _selected_predictors, _predictors_address)
print("Writing predictions to output json file")
write_dict_to_json(_output_json_file, _image_predictions_dict)
print("Finished.")
