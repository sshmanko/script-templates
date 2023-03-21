import argparse
import logging

import requests
import urllib3
import yaml
from requests.adapters import HTTPAdapter

logging.basicConfig(format='%(asctime)s %(levelname)-9s %(message)s', level=logging.INFO)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    return parser.parse_args()


def parse_conf(config_path='/etc/kvm-autotester/config.yaml') -> dict:
    try:
        with open(config_path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        logging.error(f"Unable to load/parse config file '{config_path}':\n{e}")


def retry_request(method, url, **kwargs) -> requests.Response:
    s = requests.Session()
    s.headers.update({"User-Agent": "my-awesome-script v1.0"})

    retry_obj = urllib3.util.retry.Retry(
        total=5,
        backoff_factor=3,
        allowed_methods=frozenset(["GET", "POST", "DELETE"]),
        status_forcelist=[500, 502, 503, 504],
        raise_on_status=False,
    )

    s.mount("https://", HTTPAdapter(max_retries=retry_obj))

    try:
        r = s.request(method, url, timeout=(5, 60), **kwargs)
        r.raise_for_status()
        return r
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP {e.response.status_code}: {e}")
        logging.error(e.response.text.replace("\n", " "))
    except requests.exceptions.ConnectionError as e:
        logging.error(f"Connection error: {e}")
    except Exception as e:
        logging.error(f"Undefined error: {e}")
        

def main():
    args = parse_args()
    conf = parse_conf()
    print(args, conf)


if __name__ == '__main__':
    main()
