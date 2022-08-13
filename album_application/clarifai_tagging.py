from os import listdir, path
import sys
import json
from progress.bar import IncrementalBar

USER_ID = 'user_id'
PAT = 'personal_access_token'
APP_ID = 'application_id'
MODEL_ID = 'general-image-recognition'

if len(sys.argv) < 3:
    print("To few arguments | <py_version> clarifai_classify.py <album_cover_dir> <output_file>")
    exit(-1)

if not path.isdir(sys.argv[1]):
    print("The selected directory of album covers does not exist")
    exit(-1)

album_covers = listdir(sys.argv[1])

print("Amount of files in directory: ", len(album_covers))

output_json = {}

output_file = sys.argv[2]

prog_bar = IncrementalBar("Tagging albums", max=len(album_covers))

from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2

channel = ClarifaiChannel.get_grpc_channel()
stub = service_pb2_grpc.V2Stub(channel)

metadata = (('authorization', 'Key ' + PAT),)

userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)

for cover_id in album_covers:
    try:
        file_location = sys.argv[1] + "/" + cover_id
        with open(file_location, "rb") as f:
            file_bytes = f.read()


        #*************************************************************************************
        #    Title: Images: Make predictions on image inputs                                   
        #    Author: Clarifai                                                        
        #    Date retrieved: 2022/04/23                                                        
        #    Availability: https://docs.clarifai.com/api-guide/predict/images#via-bytes                                                
        #                                                                                      
        #*************************************************************************************
        post_model_outputs_response = stub.PostModelOutputs(
            service_pb2.PostModelOutputsRequest(
                user_app_id=userDataObject,
                model_id=MODEL_ID,
                version_id=MODEL_VERSION_ID,
                inputs=[
                    resources_pb2.Input(
                        data=resources_pb2.Data(
                            image=resources_pb2.Image(
                                base64=file_bytes
                            )
                        )
                    )
                ]
            ),
            metadata=metadata
        )
        if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
            print(post_model_outputs_response.status)
            raise Exception("Post model outputs failed, status: " + post_model_outputs_response.status.description)

        output = post_model_outputs_response.outputs[0]

        output_json[cover_id] = {}
        prog_bar.next()

        # write the album cover's concepts to its dictionary
        for concept in output.data.concepts:
            output_json[cover_id][concept.name] = concept.value
    except Exception:
        print("Failed to tag all files, succeded to tag ", len(output_json), " covers")
        with open(output_file, "w+") as output:
            json.dump(output_json, output)

# output all the classifications for all album covers to a file in json format
with open(output_file, "w+") as output:
    json.dump(output_json, output)