import click

from config import REDIS, MONGO_URI


@click.group()
def cli():
    pass


@cli.command(short_help='Runs a shell in the app context.')
@click.argument('ipython_args', nargs=-1, type=click.UNPROCESSED)
def shell(ipython_args):
    import sys
    import IPython
    from IPython.terminal.ipapp import load_default_config

    from src.databases import Redis, Mongo

    ip_config = load_default_config()
    mongo = Mongo(MONGO_URI)

    redis = Redis(**REDIS)

    ctx = dict(
        redis=redis,
        mongodb=mongo.get_database()
    )

    banner = 'Python %s on %s\n' % (sys.version, sys.platform)
    if ctx:
        banner += 'Objects created:'
    for k, v in ctx.items():
        banner += '\n    {0}: {1}'.format(k, v)
    ip_config.TerminalInteractiveShell.banner1 = banner
    IPython.start_ipython(argv=ipython_args, user_ns=ctx, config=ip_config)


if __name__ == '__main__':
    shell()
