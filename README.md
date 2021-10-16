# ping2mqtt

Service that periodically ICMP-pings hosts and publishes the results in MQTT topics.

**This project is experimental and might have undesirable effects. Use it under your responsability!**

## Requirements

- Python >=3.6
- iputils/inetutils **ping** (no root required)
- Python requirements listed in [requirements.txt](requirements.txt)
- A MQTT server to publish results to
- Only tested under Linux

## Getting started

### 1) Configure the hosts to ping

The hosts can be defined in either a JSON or [NDJSON](http://ndjson.org/) file:

```json
[
    {"host": "1.1.1.1", "interval": 1},
    {"host": "8.8.8.8", "interval": 1.8},
    {"host": "208.67.222.222", "interval": 2}
]
```

```ndjson
{"host": "1.1.1.1", "interval": 1}
{"host": "8.8.8.8", "interval": 1.8}
{"host": "208.67.222.222", "interval": 2}
```

The file must be named either `hosts.json` or `hosts.ndjson`, depending on if specified as a JSON or NDJSON, respectively.

Each final JSON object within the hosts file represents a host to ping. Its attributes are:

- `host`: hostname or ip to ping (required)
- `interval`: seconds between pings (required) (accepts decimals; cannot be less than 0.2)
- `interface`: network interface to send pings through (optional)

### 2) Configure the service settings

The rest of settings, not related with the hosts to ping, are defined using environment variables, or within a .env file.
Settings defined using environment variables will override those defined on the .env file.

Refer to the [sample.env](sample.env) file for a list of the available settings and their description.

### 3) Run with Docker

This image is compatible with the [Docker-Python-Git-App](https://github.com/David-Lor/Docker-Python-Git-App) image, that will clone the repository and install the Python dependencies on container startup. This image already bundles the `ping` command.

The following command will start a container with such image, using this repository. The service settings are supposed to be in a .env file, but they could be loaded using `-e` for each setting.

```bash
cp sample.env .env
# Edit your .env file!

cp examples/hosts.ndjson .
# Put your custom hosts for pinging, or use the given examples

docker run -d --name=ping2mqtt \
    -v $(pwd)/hosts.ndjson:/hosts.ndjson \
    --env-file $(pwd)/.env \
    -e HOSTS_FILE=/hosts \
    -e GIT_REPOSITORY=https://github.com/David-Lor/ping2mqtt \
    davidlor/python-git-app
```

## Changelog

- 0.0.1
    - Initial release

## Known Issues & Future improvements

- Sometimes, ping values can be incorrect (too low or too high) - does not seem to be very common
- Improve service exit flow
