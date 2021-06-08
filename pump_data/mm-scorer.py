import argparse
import copy
from pathlib import Path
import json
import re
import requests
from time import sleep
import sys
import pandas as pd

def send_request(data, curl):
    headers = {
        'Content-Type': 'application/json',
    }
    sample = copy.deepcopy(curl["payload"])
    sample["rows"] = data
    data = json.dumps(sample)
    print("Request>> ",data)
    response = requests.post(curl["url"], headers=headers, data=data)
    if response.status_code == 200:
        print("Response>>", response.json(), "\n")
    else:
        print("Response>>", response)
    return response.json()


def setup(curl_file):
    curl = dict()
    with open(curl_file) as file:
        curl_data = file.read().replace('\n', '').split("EOF")
    curl["payload"] = json.loads(curl_data[1])
    curl["fields"] = curl["payload"]["fields"]
    curl["url"] = re.search("(?P<url>https?://[^\s]+)", curl_data[0]).group("url")
    return curl

def pump(data, curl):
    while True:
        for index, row in data.iterrows():
            data = row[curl["fields"]].values.tolist()
            data = list(map(str, data))
            send_request([data], curl)
            sleep(2)
        
def score(data, curl, op):
    batch_size = 5
    raw_data = list()
    request_data = list()

    pd.DataFrame(columns=list(data.columns)+['score']).to_csv(op)
    for index, row in data.iterrows():
        raw_data.append(row.values.tolist())
        _data = row[curl["fields"]].values.tolist()
        request_data.append(list(map(str, _data)))
        print(index, len(request_data), len(raw_data))
        if len(request_data) == batch_size:   
            score_and_save(raw_data, request_data, curl, op)
            print("Calling")         
            request_data = list()
            raw_data = list()
    score_and_save(raw_data, request_data, curl, op)

def score_and_save(raw_data, request_data, curl, op):
    response_data = send_request(request_data, curl)['score']
    print("----", len(request_data), len(raw_data), len(response_data))
    print(response_data)
    print(raw_data)
    df = pd.concat([pd.DataFrame(raw_data),pd.DataFrame(response_data)], axis=1)
    
    df.to_csv(op, mode='a', header=False)
    print(df)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", type=str, choices=["score", "pump"],
                        help="Choose the required action. 'score': to get the scored values back. 'pump': to simulate traffic to the Model Manager")
    parser.add_argument("curl_file", type=str, 
                        help="Path to a sample curl file to the end point")
    parser.add_argument("data_file", type=str, 
                        help="CSV file with sample data")
    args = parser.parse_args()

    curl_file = Path(args.curl_file)
    if not curl_file.is_file():
        print(f"CSV file '{curl_file}'' does not exist.")
        sys.exit(0)

    data_file = Path(args.data_file)
    if not data_file.is_file():
        print(f"Data file '{data_file}'' does not exist.")
        sys.exit(0)
    return args

def main():
    args = get_args()
    curl = setup(args.curl_file)
    data = pd.read_csv(args.data_file)
    data.fillna(0, inplace=True)


    if args.action == 'score':
        score(data, curl, "score_"+args.data_file)
    else:
        pump(data, curl)

if __name__ == '__main__':
    main()
