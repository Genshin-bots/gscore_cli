import os
import subprocess
from pathlib import Path
from typing import List

import httpx
import questionary
import typer
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn

core_git_url = "https://github.com/Genshin-bots/gsuid_core.git"
plugin_list_url = 'https://docs.sayu-bot.com/plugin_list.json'

git_extra = '--depth=1 --single-branch'

install_core_path = Path.cwd()
gscore_path = install_core_path / 'gsuid_core'
install_plugin_path = gscore_path / 'gsuid_core' / 'plugins'


ascii_code = """

    //   ) )                                 //   ) )
   ((         ___                           //         ___      __      ___
     \\     //   ) ) //   / / //   / /     //        //   ) ) //  ) ) //___) )
       ) ) //   / / ((___/ / //   / /     //        //   / / //      //
((___ / / ((___( (      / / ((___( (     ((____/ / ((___/ / //      ((____     """  # noqa: W291, E501, W293


def main():
    print(ascii_code)
    print("\n")
    print("✨ 欢迎使用[bold red]GsCore[/bold red] - [green]早柚核心[/green]！")

    get_env = (
        questionary.select(
            "将使用何种环境启动GsCore?",
            choices=[
                "pdm",
                "poetry",
                "不需要虚拟环境",
            ],
            default="poetry",
            qmark='❓',
            instruction='(使用【方向键】选择, 【回车键】确定)',
        ).ask(),
    )[0]

    print('❓ 正在为你检查环境是否已安装完成...')
    g_proc = subprocess.run(
        args='git -v',
        cwd=install_core_path,
        capture_output=True,
        text=True,
    )
    if g_proc.stdout.startswith('git version'):
        print('✅ 你已正确安装git!')

    if get_env != '不需要虚拟环境':
        if get_env == 'pdm':
            t_proc = subprocess.run(
                args='pdm -V',
                cwd=install_core_path,
                capture_output=True,
                text=True,
            )
            if t_proc.stdout.startswith('PDM, version'):
                print('✅ 你已正确安装pdm!')
        else:
            t_proc = subprocess.run(
                args='poetry -V',
                cwd=install_core_path,
                capture_output=True,
                text=True,
            )
            if t_proc.stdout.startswith('Poetry (version'):
                print('✅ 你已正确安装poetry!')
    else:
        get_env = 'pip'

    print('✅ 环境检查流程已通过！')

    print("🚀 正在为你安装GsCore至[bold red]当前目录[/bold red]......")
    get_proxy = (
        questionary.select(
            "使用代理Git站进行Clone?",
            choices=[
                "不需要",
                "https://ghproxy.fuckmys.tk/",
                "https://mirror.ghproxy.com/",
                "https://ghproxy.com/",
            ],
            default="https://ghproxy.fuckmys.tk/",
            qmark='❓',
            instruction='(使用【方向键】选择, 【回车键】确定)',
        ).ask(),
    )

    _proxy = get_proxy[0]
    if _proxy == "不需要":
        proxy = ''
    else:
        proxy = _proxy

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="安装中...", total=None)
        cmd = f"git clone {proxy}{core_git_url} {git_extra}"
        proc = subprocess.run(
            args=cmd,
            cwd=install_core_path,
            capture_output=True,
            text=True,
        )

    if proc.returncode != 0:
        print("❌ [bold red]安装失败, 可能是网络原因[/bold red]......")
        return
    else:
        print("🚀 [bold green]安装成功[/bold green]!")

    is_install_plugin = (
        questionary.select(
            "是否现在开始安装插件?",
            choices=[
                "是的",
                "不需要",
            ],
            default='是的',
            qmark='❓',
            instruction='(使用【方向键】选择, 【回车键】确定)',
        ).ask(),
    )

    if is_install_plugin[0] == '是的':
        _plugins_list = httpx.get(plugin_list_url).json()
        plugins = _plugins_list['plugins']
        plugins_choices = [f'{i} | {plugins[i]["info"]}' for i in plugins]
        install_plugins: List[str] = questionary.checkbox(
            '选择要安装的插件',
            choices=plugins_choices,
            instruction='(使用【方向键】移动,【空格键】选择,【回车键】确定)',
        ).ask()

        for i in install_plugins:
            plugin_name = i.split(' | ')[0]
            plugin = plugins[plugin_name]
            url = plugin['link']
            branch = plugin['branch']
            plugin_cmd = f"git clone {proxy}{url} -b {branch} {git_extra}"
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                progress.add_task(description="安装中...", total=None)
                p_proc = subprocess.run(
                    args=plugin_cmd,
                    cwd=install_plugin_path,
                    capture_output=True,
                    text=True,
                )
                if p_proc.returncode != 0:
                    _error = '安装失败, 可能是网络原因。'
                    print(f"❌ [bold red]{plugin_name} {_error}[/bold red]")
                else:
                    print(f"✅ [bold green]{plugin_name} 安装成功！[/bold green]")

    install_dep: bool = questionary.confirm(
        "现在开始安装依赖？",
        qmark='❓',
    ).ask()

    if install_dep:
        if get_env == 'pip':
            dep_cmd = 'pip install -r requirements.txt'
        else:
            dep_cmd = f'{get_env} install'

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf8"

        d_proc = subprocess.run(
            args=dep_cmd,
            cwd=gscore_path,
            capture_output=True,
            text=True,
            env=env,
        )
        if d_proc.returncode != 0:
            error = '安装失败, 可能是网络原因。'
            print(f"❌[bold red] {error}[/bold red]")
        else:
            print("✅ [bold green]依赖安装成功！[/bold green]")

    print('🔨 现在开始进行初始化配置...')

    answers = questionary.form(
        second=questionary.select(
            "使用代理Git站进行Clone?",
            choices=[
                "不需要",
                "https://ghproxy.fuckmys.tk/",
                "https://mirror.ghproxy.com/",
                "https://ghproxy.com/",
            ],
            qmark='❓',
            instruction='(使用【方向键】移动,【回车键】确定)',
        ),
    ).ask()

    print(answers)
    print("[bold red]🎉恭喜!安装已全部完成！[/bold red]")


if __name__ == "__main__":
    typer.run(main)
