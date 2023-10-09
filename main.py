import transformers
import os
import requests
from gql_queries import getAudioFile, getJSONDocument, getProject
import pandas as pd
import json

# Obtain from URL on Voxtir platform
PROJECT_ID = ""
# inspect the requests in the network tab of the browser
AUTH_0_TOKEN=""

# Default API setup
API_URL="https://api.staging.voxtir.com"
headers = {
    "Content-Type": "application/json",
    "Origin": "https://app.staging.voxtir.com",
    "Authorization": "Bearer {AUTH_0_TOKEN}",  # Replace with your actual Bearer token
}

headers = {"Authorization": f"Bearer {AUTH_0_TOKEN}"}

def run_query(query, variables): # A simple function to use requests.post to make the API call. Note the json= section.
    request = requests.post(f'{API_URL}/graphql', json={'query': query, 'variables': variables}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

# Fetch Data
data = []
projectData = run_query(getProject, {"projectId": PROJECT_ID})
for document in projectData["data"]["project"]["documents"]:
    if (document["transcriptionStatus"] != "DONE") or (document["transcriptionType"] != "AUTOMATIC"):
        continue
    documentId = document["id"]
    # Get the audio file
    res = run_query(getAudioFile, {"documentId": documentId})
    presignedUrl = res["data"]["getPresignedUrlForAudioFile"]["url"]
    # Download the audio file
    r = requests.get(presignedUrl)
    # Save the audio file - All files are mp3 - 
    audio_file = f"output/audio/raw/{documentId}.mp3"
    with open(audio_file, "wb") as f:
        f.write(r.content)
    # Get the JSON document
    res = run_query(getJSONDocument, {"documentId": documentId})
    # Save the JSON document
    data_file = f"output/json/{documentId}.json"
    with open(data_file, "w") as f:
        f.write(res["data"]["documentJSON"])
    
    # Add to data
    data.append(
        {
            "id": documentId,
            "transcriptionType": document["transcriptionType"],
            "transcriptionStatus": document["transcriptionStatus"],
            "audio": audio_file,
            "json": data_file
        }
    )
    break

# Create a dataframe
df = pd.DataFrame(data)
# Add headers
df.columns = ["id", "transcriptionType", "transcriptionStatus", "audio", "json"]
# Save to CSV
df.to_csv("data.csv", index=False)

# Generate the dataset. Does not take too long pr. audio file. O(n) where n is the length of the audio file for each audio file.
last_timestamp_at=0
text_collection = ""
dataset = []
for idx, row in df.iterrows():
    jsondata = json.load(open(row["json"]))
    for section in jsondata["default"]["content"]:
        for node in section["content"]:
            if node["type"] == "text":
                for child in node["content"]:
                    if child["type"] == "text":
                        text_collection += child["text"]
                    if child["type"] == "timeStampButton":
                        # hh:mm:ss.ms
                        timestamp_str=child["attrs"]["timestamp"]
                        timestamp_seconds = int(timestamp_str.split(":")[0])*3600 + int(timestamp_str.split(":")[1])*60 + int(timestamp_str.split(":")[2].split(".")[0])
                        
                        # Whisper works on 30 second intervals
                        if timestamp_seconds - last_timestamp_at > 30:
                            text_collection = ""
                            last_timestamp_at = timestamp_seconds
                            continue
                        # Extract the audio with ffmpeg
                        file_name = f"output/audio/{row['id']}_{last_timestamp_at}_{timestamp_str}.mp3"
                        command = f"ffmpeg -ss {last_timestamp_at} -i {row['audio']} -t {timestamp_seconds-last_timestamp_at} {file_name}"

                        dataset.append(
                            {
                                "text": text_collection,
                                "audio": file_name,
                                "start": last_timestamp_at,
                                "end": timestamp_seconds,
                                "duration": timestamp_seconds-last_timestamp_at,
                                "original": row["audio"]

                            }
                        )


# Create the huggingface dataset

# Fine-tune the model



            


