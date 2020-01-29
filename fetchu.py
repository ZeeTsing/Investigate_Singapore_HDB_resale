from concurrent.futures import as_completed
from requests_futures.sessions import FuturesSession

responses = {}

def response_hook(resp, *args, **kwargs):
    if resp.status_code not in responses:
        responses[resp.status_code] = [resp.url]
    else:
        responses[resp.status_code].append([resp.url])

def fetch_url (url_path, name, headers=None,workers=50):
    '''The function takes in a list of url and fetch accordingly;
    It returns three files: "success_name.txt", "failure_name.txt" and "done_name.txt"
    information fetched is stored in success and failure stores urls that failed to be fetched
    done stores the list of url that was successfully fetched '''
    hooks = { 'response' : response_hook }
    with FuturesSession(max_workers=workers) as session:
        futures = []
        with open(url_path) as url_file:
            for url in url_file:
                futures.append(session.get(url[:-1], headers=headers))

        done = 0
        success = 0
        failure = 0
        with open(f'success_{name}.txt', 'a') as success_file:
            with open(f'failure_{name}.txt', 'a') as failure_file:
                with open(f'done_{name}.txt', 'a') as done_file:
                    for future in as_completed(futures):
                        resp = future.result()
                        done_file.write("{}\n".format(resp.url))

                        if resp.status_code == 200 and len(resp.text) > 49:
                            success_file.write('{"url": ' +str(resp.url)+ ', "text": ' +resp.text+ '}\n')
                            success += 1
                        else:
                            failure_file.write('{"url": ' +str(resp.url)+ ', "error": ' +str(resp.status_code)+ '}\n')
                            failure += 1

                        done += 1
                        print("Done: {}/{}, Success: {}, Failure: {}".format(done, len(futures), success, failure))
