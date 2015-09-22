import os
import json
import requests
import auth
from exceptions import AlaudaException
from exceptions import AlaudaInputError
import settings
import util

SSH = 'ssh'
PLINK = 'plink'
DEFAULT_EXEC_ENDPOINT = 'exec.alauda.cn'
VERBOSE = False

def execute(ssh_client, namespace, is_verbose, container, command_list):

    if isinstance(is_verbose, bool):
        global VERBOSE
        VERBOSE = is_verbose

    if not namespace:
        try:
            _, _, username = auth.load_token()
            namespace = username
        except:
            raise AlaudaInputError('Please login first or specify namespace')

    ssh_client, ssh_client_location = parse_ssh_client_arg(ssh_client)
    exec_endpoint = get_exec_endpoint(namespace, container)

    args = (ssh_client_location, namespace, exec_endpoint, container, ' '.join(command_list))

    if ssh_client == SSH:
        # ssh -p 4022 -t USER@exec.alauda.cn CONTAINER COMMAND
        exec_command = '{0} -p 4022 -t {1}@{2} {3} {4}'.format(*args)
    elif ssh_client == PLINK:
        # plink -P 4022 -t USER@exec.alauda.cn CONTAINER COMMAND
        exec_command = '{0} -P 4022 -t {1}@{2} {3} {4}'.format(*args)

    verbose('namespace: {0}'.format(namespace))
    verbose('ssh client: {0}'.format(ssh_client))
    verbose('the path of ssh client: {0}'.format(ssh_client_location))
    verbose('command: {0}'.format(exec_command))

    os.system(exec_command)

def parse_ssh_client_arg(ssh_client):
    assert isinstance(ssh_client, str)

    ssh_client_location = None
    if ':' in ssh_client:
        arg_split = ssh_client.split(':')
        ssh_client = arg_split[0]
        if len(arg_split) > 1:
            ssh_client_location = ':'.join(arg_split[1:])
        if ssh_client_location is not None and len(ssh_client_location.strip()) == 0:
            raise AlaudaInputError('invalid location of ssh client, only support ssh and plink.')
    else:
        ssh_client_location = ssh_client

    if ssh_client not in (SSH, PLINK):
        raise AlaudaInputError('invalid ssh client')

    return ssh_client, ssh_client if ssh_client_location is None else ssh_client_location


def parse_container_arg(container):
    if '.' not in container:
        service_name = container
        container_number = 0
    else:
        arg_split = container.split('.')
        try:
            container_number = int(arg_split[-1])
            service_name = '.'.join(arg_split[:-1])
        except:
            service_name = container
            container_number = 0
    return service_name, container_number


def get_exec_endpoint(namespace, container):

    try:
        _, _, username = auth.load_token()
        if namespace != username:
            verbose('use default exec endpoint: {0}'.format(DEFAULT_EXEC_ENDPOINT))
            return DEFAULT_EXEC_ENDPOINT
    except:
        verbose('use default exec endpoint: {0}'.format(DEFAULT_EXEC_ENDPOINT))
        return DEFAULT_EXEC_ENDPOINT

    service_name, _ = parse_container_arg(container)
    verbose('service name: {0}'.format(service_name))

    try:
        exec_endpoint = load_exec_endpoint(service_name)
    except:
        api_endpoint, token, username = auth.load_token()
        url = api_endpoint + '/services/{0}/{1}'.format(namespace, service_name)
        headers = auth.build_headers(token)

        r = requests.get(url, headers=headers)
        util.check_response(r)
        data = json.loads(r.text)
        exec_endpoint = data['exec_endpoint']

        save_exec_endpoint(service_name, exec_endpoint)

    return exec_endpoint


def save_exec_endpoint(service_name, exec_endpoint):
    try:
        with open(settings.ALAUDACFG, 'r') as f:
            config = json.load(f)
    except:
        config = {}
    config.setdefault('exec_endpoint', {})
    config['exec_endpoint'][service_name] = exec_endpoint

    with open(settings.ALAUDACFG, 'w') as f:
        json.dump(config, f, indent=2)

def load_exec_endpoint(service_name):
    try:
        with open(settings.ALAUDACFG, 'r') as f:
            config = json.load(f)
            exec_endpoint = config['exec_endpoint'][service_name]
            return exec_endpoint
    except:
        raise AlaudaException('Error occured while loading exec endpoint')

def verbose(message):
    global VERBOSE
    if VERBOSE:
        print '[alauda info] {0}'.format(message)