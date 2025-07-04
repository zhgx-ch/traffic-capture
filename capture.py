import typer
import subprocess
import sys
sys.path.append(".")
from mac_proxy import proxy_on,proxy_off

app = typer.Typer(name="capture")
MITMPROXY_SCRIPT = "mitmproxy_recorder.py"


@app.command(name="record", help="start record capture")
def record(
    url_filter: str = typer.Option("", help="只录制包含此字符串的URL"),
    port: int = typer.Option(8080, help="mitmproxy监听端口")
):
    """
    开始录制流量，自动打开和关闭系统代理
    """
    try:
        proxy_on()
        typer.echo("代理已开启，开始录制...")

        # 启动 mitmproxy，加载脚本
        mitm_cmd = [
            "mitmproxy",
            "-s", MITMPROXY_SCRIPT,
            "-p", str(port)
        ]
        typer.echo("获取到过滤网址为 " + url_filter)
        if url_filter:
            mitm_cmd += ["--set", f"url_filter={url_filter}"]
        typer.echo("指令为 " + " ".join(mitm_cmd))
        proc = subprocess.Popen(mitm_cmd)
        proc.wait()
    except KeyboardInterrupt:
        typer.echo("录制结束，正在关闭代理...")
        proxy_off()
        typer.echo("代理已关闭。")
        if proc and proc.poll() is None:
            proc.terminate()
    except Exception as e:
        typer.echo(f"发生错误: {e}")
        proxy_off()
        if proc and proc.poll() is None:
            proc.terminate()
    finally:
        proxy_off()
        typer.echo("流程已结束。")

if __name__ == "__main__":
    app()
