import os
import yaml
from itertools import cycle
from loguru import logger
from src.main import Parser


def validate_settings() -> tuple[str | None, int]:
    events_limit = config.get("events_limit")
    timeout = config.get("timeout")

    if not events_limit or not isinstance(events_limit, int):
        raise ValueError("Events limit in settings must be an integer")

    if not timeout or not isinstance(timeout, int):
        raise ValueError("Timeout in settings must be an integer")

    if config.get("use_proxy"):
        proxies_path = os.path.join(os.getcwd(), "proxies.txt")
        if os.path.exists(proxies_path) and os.path.getsize(proxies_path) > 0:
            with open(proxies_path, "r") as proxies_file:
                proxies = proxies_file.read().splitlines()

            for proxy in proxies:
                parts = proxy.split(":")
                if len(parts) != 4:
                    raise ValueError("Proxy must be in format ip:port:user:password")

            return proxies_path, events_limit
        else:
            raise FileNotFoundError("Proxies file not found or empty")
    else:
        return None, events_limit


def run():
    proxies_path, events_limit = validate_settings()

    if proxies_path and config.get("use_proxy"):
        with open(proxies_path, "r") as proxies_file:
            proxies = proxies_file.read().splitlines()

        proxy_cycle = cycle(proxies)
        while True:
            proxy = next(proxy_cycle)
            logger.info(f"Parser started | Proxy: {proxy}")
            parser = Parser(events_limit=events_limit, proxy=proxy, timeout=config["timeout"])
            parser.run()

    else:
        while True:
            logger.info("Parser started | Proxy: None")
            parser = Parser(events_limit=events_limit, timeout=config["timeout"])
            parser.run()


if __name__ == "__main__":
    with open("settings.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)

    run()
