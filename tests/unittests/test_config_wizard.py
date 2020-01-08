import pytest
from click.testing import CliRunner
from typing import Dict
import os
from pathlib import Path

from faraday_agent_dispatcher.cli.main import config_wizard
from faraday_agent_dispatcher import config as config_mod
from tests.unittests.configuration import ExecutorConfig, DispatcherConfig, ParamConfig, VarEnvConfig, ADMType


def generate_configs():
    return [
        # 0 All default
        {
            "config": DispatcherConfig(),
            "exit_code": 0,
            "after_executors": set()
        },
        # 1 Dispatcher config
        {
            "config": DispatcherConfig(host="127.0.0.1", api_port="13123", ws_port="1234", workspace="aworkspace",
                                       agent_name="agent", registration_token="1234567890123456789012345"),
            "exit_code": 0,
            "after_executors": set()
        },
        # 2 Bad token config
        {
            "config": DispatcherConfig(host="127.0.0.1", api_port="13123", ws_port="1234", workspace="aworkspace",
                                       agent_name="agent", registration_token=["12345678901234567890", ""]),
            "exit_code": 0,
            "expected_outputs": ["registration must be 25 character length"],
            "after_executors": set()
        },
        # 3 Basic Executors config
        {
            "config": DispatcherConfig(),
            "executors_config": [
                    ExecutorConfig(name="ex1",
                                   cmd="cmd 1",
                                   params=[
                                       ParamConfig(name="add_param1", value=True, adm_type=ADMType.ADD),
                                       ParamConfig(name="add_param2", value=False, adm_type=ADMType.ADD)
                                   ],
                                   adm_type=ADMType.ADD),
                    ExecutorConfig(name="ex2",
                                   cmd="cmd 2",
                                   varenvs=[
                                       VarEnvConfig(name="add_varenv1", value="AVarEnv", adm_type=ADMType.ADD)
                                   ],
                                   adm_type=ADMType.ADD),
                    ExecutorConfig(name="ex3",
                                   cmd="cmd 3",
                                   params=[
                                       ParamConfig(name="add_param1", value=True, adm_type=ADMType.ADD),
                                       ParamConfig(name="add_param2", value=False, adm_type=ADMType.ADD)
                                   ],
                                   varenvs=[
                                       VarEnvConfig(name="add_varenv1", value="AVarEnv", adm_type=ADMType.ADD)
                                   ],
                                   adm_type=ADMType.ADD),
                ],
            "exit_code": 0,
            "after_executors": {"ex1", "ex2", "ex3"}
        },
        # 4 Basic Bad Executors config
        {
            "config": DispatcherConfig(),
            "executors_config": [
                    ExecutorConfig(name="ex1",
                                   cmd="cmd 1",
                                   params=[
                                       ParamConfig(name="add_param1", value=True, adm_type=ADMType.ADD),
                                       ParamConfig(name="add_param2", value=False, adm_type=ADMType.ADD)
                                   ],
                                   adm_type=ADMType.ADD),
                    ExecutorConfig(name="ex2",
                                   cmd="cmd 2",
                                   varenvs=[
                                       VarEnvConfig(name="add_varenv1", value="AVarEnv", adm_type=ADMType.ADD)
                                   ],
                                   adm_type=ADMType.ADD),
                    ExecutorConfig(name="ex3",
                                   cmd="cmd 3",
                                   params=[
                                       ParamConfig(name="add_param1", value=True, adm_type=ADMType.ADD),
                                       ParamConfig(name="add_param2", value=False, adm_type=ADMType.ADD)
                                   ],
                                   varenvs=[
                                       VarEnvConfig(name="add_varenv1", value="AVarEnv", adm_type=ADMType.ADD)
                                   ]
                                   , adm_type=ADMType.ADD),
                    ExecutorConfig(error_name="ex1",
                                   cmd="cmd 4",
                                   name="ex4",
                                   params=[
                                       ParamConfig(name="add_param1", value=True, adm_type=ADMType.ADD),
                                       ParamConfig(name="add_param2", value=False, adm_type=ADMType.ADD)
                                   ],
                                   varenvs=[
                                       VarEnvConfig(name="add_varenv1", value="AVarEnv", adm_type=ADMType.ADD)
                                   ],
                                   adm_type=ADMType.ADD),
                ],
            "exit_code": 0,
            "after_executors": {"ex1", "ex2", "ex3", "ex4"}
        },
        # 5 Basic Mod Executors config
        {
            "config": DispatcherConfig(),
            "executors_config": [
                    ExecutorConfig(name="ex1",
                                   cmd="cmd 1",
                                   params=[
                                       ParamConfig(name="add_param1", value=True, adm_type=ADMType.ADD),
                                       ParamConfig(name="add_param2", value=False, adm_type=ADMType.ADD)
                                   ],
                                   adm_type=ADMType.ADD),
                    ExecutorConfig(name="ex2",
                                   cmd="cmd 2",
                                   varenvs=[
                                       VarEnvConfig(name="add_varenv1", value="AVarEnv", adm_type=ADMType.ADD)
                                   ],
                                   adm_type=ADMType.ADD),
                    ExecutorConfig(name="ex3", cmd="cmd 3",
                                   params=[
                                       ParamConfig(name="add_param1", value=True, adm_type=ADMType.ADD),
                                       ParamConfig(name="add_param2", value=False, adm_type=ADMType.ADD)
                                   ],
                                   varenvs=[
                                       VarEnvConfig(name="add_varenv1", value="AVarEnv", adm_type=ADMType.ADD)
                                   ],
                                   adm_type=ADMType.ADD),
                    ExecutorConfig(name="ex1",
                                   error_name="QWE",
                                   cmd="exit 1",
                                   params=[
                                       ParamConfig(name="mod_param1", value=True, adm_type=ADMType.ADD),
                                       ParamConfig(name="add_param1", value=False, adm_type=ADMType.MODIFY)
                                   ],
                                   adm_type=ADMType.MODIFY),
                    ExecutorConfig(name="ex2",
                                   cmd="",
                                   varenvs=[
                                       VarEnvConfig(name="mod_varenv1", value="AVarEnv", adm_type=ADMType.ADD)
                                   ],
                                   adm_type=ADMType.MODIFY),
                    ExecutorConfig(name="ex3",
                                   new_name="eX3",
                                   cmd="",
                                   varenvs=[
                                       VarEnvConfig(name="add_varenv1", value="AVarEnv", adm_type=ADMType.MODIFY)
                                   ],
                                   adm_type=ADMType.MODIFY),
                ],
            "exit_code": 0,
            "after_executors": {"ex1", "ex2", "ex3"}
        },
        # 6 Basic Del Executors config
        {
            "config": DispatcherConfig(),
            "executors_config": [
                    ExecutorConfig(name="ex1",
                                   cmd="cmd 1",
                                   params=[
                                       ParamConfig(name="add_param1", value=True, adm_type=ADMType.ADD),
                                       ParamConfig(name="add_param2", value=False, adm_type=ADMType.ADD)
                                   ],
                                   adm_type=ADMType.ADD),
                    ExecutorConfig(name="ex2",
                                   cmd="cmd 2",
                                   varenvs=[
                                       VarEnvConfig(name="add_varenv1", value="AVarEnv", adm_type=ADMType.ADD)
                                   ],
                                   adm_type=ADMType.ADD),
                    ExecutorConfig(name="ex3", cmd="cmd 3",
                                   params=[
                                       ParamConfig(name="add_param1", value=True, adm_type=ADMType.ADD),
                                       ParamConfig(name="add_param2", value=False, adm_type=ADMType.ADD)
                                   ],
                                   varenvs=[
                                       VarEnvConfig(name="add_varenv1", value="AVarEnv", adm_type=ADMType.ADD)
                                   ],
                                   adm_type=ADMType.ADD),
                    ExecutorConfig(name="ex1",
                                   error_name="QWE",
                                   cmd="exit 1",
                                   params=[
                                       ParamConfig(name="add_param1", value=False, adm_type=ADMType.DELETE)
                                   ],
                                   adm_type=ADMType.MODIFY),
                    ExecutorConfig(name="ex2",
                                   cmd="",
                                   adm_type=ADMType.DELETE),
                    ExecutorConfig(name="ex3",
                                   new_name="eX3",
                                   cmd="",
                                   varenvs=[
                                       VarEnvConfig(name="add_varenv1", value="AVarEnv", adm_type=ADMType.MODIFY)
                                   ],
                                   adm_type=ADMType.MODIFY),
                ],
            "exit_code": 0,
            "after_executors": {"ex1", "ex3"}
        },
    ]


def old_version_path():
    return Path(__file__).parent.parent / 'data' / 'old_version_inis'


configs = generate_configs()
ini_configs = \
    [
        {
            "dir": "",
            "old_executors": set()
        },
        {
            "dir": old_version_path() / '0.1.ini',
            "old_executors": {"default"}
        }
    ]


def parse_config(config: Dict):
    output = ""
    if "config" in config:
        dispatcher_config: DispatcherConfig = config['config']
        output = f"A\n{dispatcher_config.config_str()}"
    if "executors_config" in config:
        executors_config = config["executors_config"]
        output = f"{output}E\n"
        for executor_conf in executors_config:
            output = f"{output}{executor_conf.config_str()}"
        output = f"{output}Q\n"
    output = f"{output}Q\n"
    return output


@pytest.mark.parametrize(
    "testing_configs",
    configs
)
@pytest.mark.parametrize(
    "ini_config",
    ini_configs
)
def test_new_config(testing_configs: Dict[(str, object)], ini_config):
    runner = CliRunner()

    content = None
    content_path = ini_config["dir"]

    if content_path != "":
        with open(content_path, 'r') as content_file:
            content = content_file.read()

    with runner.isolated_filesystem() as file_system:

        if content:
            path = Path(file_system) / "dispatcher.ini"
            with path.open(mode="w") as content_file:
                content_file.write(content)
        else:
            path = Path(file_system)
        in_data = parse_config(testing_configs) + "\0\n" * 1000  # HORRIBLE FIX
        env = os.environ
        env["DEFAULT_VALUE_NONE"] = "True"
        result = runner.invoke(config_wizard, args=["-c", path], input=in_data, env=env)
        assert result.exit_code == testing_configs["exit_code"], result.exception
        if "exception" in testing_configs:
            assert str(result.exception) == str(testing_configs["exception"])
            assert result.exception.__class__ == testing_configs["exception"].__class__
        else:
            assert '\0\n' not in result.output
        if "expected_outputs" in testing_configs:
            for expected_output in testing_configs["expected_outputs"]:
                assert expected_output in result.output

        expected_executors_set = set.union(ini_config["old_executors"], testing_configs["after_executors"])
        if "default" in expected_executors_set:
            expected_executors_set.remove("default")
            expected_executors_set.add(config_mod.DEFAULT_EXECUTOR_VERIFY_NAME)

        config_mod.reset_config(path)
        executor_config_set = set(config_mod.instance.get(config_mod.Sections.AGENT, "executors").split(","))
        if '' in executor_config_set:
            executor_config_set.remove('')
        assert executor_config_set == expected_executors_set
