import csv
import datetime
import json
import logging
import requests
import sys
import time


def main():

    network = sys.argv[1]
    lookback_in_days = int(sys.argv[2])

    referenda_url = f"https://{network}.api.subscan.io/api/scan/referenda/referendums"
    payload = {"page": 0, "row": 1}
    response = requests.post(url=referenda_url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
    latest_referendum_index = json.loads(response.text)['data']['list'][0]['referendum_index']
    current_referendum_index = json.loads(response.text)['data']['list'][0]['referendum_index']
    referendum_index_origin_map = [(latest_referendum_index,
                                    {'origins_id': json.loads(response.text)['data']['list'][0]['origins_id'],
                                    'origins': json.loads(response.text)['data']['list'][0]['origins']})]

    cutoff_time = int(datetime.datetime.timestamp(datetime.datetime.utcnow() - datetime.timedelta(days=lookback_in_days)))
    referendum_time = json.loads(response.text)['data']['list'][0]['created_block_timestamp']

    logging.info(f'Finding earliest referendum that was <= {lookback_in_days} days ago')
    while referendum_time > cutoff_time:
        current_referendum_index -= 1
        logging.info(f'Current referendum index is {current_referendum_index}')
        referendum_url = f"https://{network}.api.subscan.io/api/scan/referenda/referendum"
        response = requests.post(url=referendum_url, headers={'Content-Type': 'application/json'}, data=json.dumps({'referendum_index': current_referendum_index}))
        referendum_index_origin_map.append((current_referendum_index,
                                    {'origins_id': json.loads(response.text)['data']['origins_id'],
                                    'origins': json.loads(response.text)['data']['origins']}))
        referendum_time = json.loads(response.text)['data']['created_block_timestamp']
        time.sleep(2)

    logging.info(f'Getting voting data for referenda {current_referendum_index}-{latest_referendum_index}')
    addresses = []
    for referendum_index in range(current_referendum_index, latest_referendum_index):
        logging.info(f'Fetching voting data for {referendum_index}...')
        address_list = True
        csv_headers = ['referendum_index','origin','address','amount','conviction','votes','status','voting_time','delegate']
        origin = next((ref for ref in referendum_index_origin_map if ref[0] == referendum_index))[1]['origins']

        i = 0
        while address_list is not None:
            payload = {
                "page": i,
                "referendum_index": referendum_index,
                "row": 100,
                "sort": "votes",
            }
            headers = {'Content-Type': 'application/json'}

            votes_url = f"https://{network}.api.subscan.io/api/scan/referenda/votes"
            response = requests.post(url=votes_url, headers=headers, data=json.dumps(payload))
            address_list = json.loads(response.text)['data']['list']
            if address_list:
                for entry in address_list:
                    entry['origin'] = origin
                    entry['address'] = entry['account']['address']
                    del entry['account']
                    entry['delegate'] = None
                    if entry['delegate_account']:
                        entry['delegate'] = entry['delegate_account']['address']
                    sanitized_entry = {}
                    for header in csv_headers:
                        sanitized_entry[f'{header}'] = entry[f'{header}']
                    addresses.append(sanitized_entry)
            i += 1
            time.sleep(2)
    
    logging.info(f'Data collection complete, {len(addresses)} voting extrinsics collected')
    current_date = datetime.datetime.utcnow().strftime("%Y%m%d")
    filename = f'{current_date}_{network}_{lookback_in_days}_days.csv'
    logging.info(f'Writing to {filename}')

    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
        writer.writeheader()
        for entry in addresses:
            writer.writerow(entry)


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO
    )
    main()
