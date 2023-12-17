import subprocess
from pathlib import Path

import questionary
import typer
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn

core_git_url = "https://github.com/Genshin-bots/gsuid_core.git"
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
    print("🚀 正在为你安装GsCore至[bold red]当前目录[/bold red]......")
    proxy = (
        questionary.select(
            "使用代理Git站进行Clone?",
            choices=[
                "不需要",
                "https://ghproxy.fuckmys.tk/",
                "https://mirror.ghproxy.com/",
                "https://ghproxy.com/",
            ],
        ).ask(),
    )

    proxy = proxy[0]
    if proxy == "不需要":
        url = core_git_url
    else:
        url = f"{proxy}{core_git_url}"

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="安装中...", total=None)
        cmd = f"git clone {url} --depth=1"
        proc = subprocess.run(
            args=cmd,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

    print(proc.returncode)
    if proc.returncode != 0:
        print("❌[bold red]安装失败, 可能是网络原因[/bold red]......")
        return
    else:
        print("🚀[bold green]安装成功[/bold green]!开始进行配置...")

    answers = questionary.form(
        second=questionary.select(
            "使用代理Git站进行Clone?",
            choices=[
                "不需要",
                "https://ghproxy.fuckmys.tk/",
                "https://mirror.ghproxy.com/",
                "https://ghproxy.com/",
            ],
        ),
    ).ask()
    print(answers)
    print("[bold red]🎉恭喜!安装已全部完成！[/bold red]")


if __name__ == "__main__":
    typer.run(main)
