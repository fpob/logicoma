import multiprocessing
import os
import re
import time

import click

from . import anidb
from . import ed2k


class UtcDate(click.ParamType):
    """
    AniDB Date parameter.

    Converts local time to server (UTC) time.
    """

    name = 'utc_date'

    FROM_STR_DATE = (
        (re.compile(r"^\d{4}-\d{2}-\d{2}$"),
         "%Y-%m-%d"),
        (re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$"),
         "%Y-%m-%d %H:%M"),
        (re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"),
         "%Y-%m-%d %H:%M:%S")
    )

    @classmethod
    def from_str(cls, date_time, _format=None):
        """Create UTC timestamp from string.

        Returns int or None if string cannot be parsed.
        """
        if date_time == "now":
            return int(time.time())
        elif _format:
            # mktime vytvari timestamp v lokalni zone
            local_dt = time.mktime(time.strptime(date_time, _format))
            return int(local_dt - time.timezone)
        else:
            for cre, fmt in cls.FROM_STR_DATE:
                if cre.match(date_time):
                    return cls.from_str(date_time, fmt)
        return None

    def convert(self, value, param, ctx):
        if value is None:
            return
        date = self.from_str(value)
        if date is None:
            self.fail('Invalid value')
        return date


def ping(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return

    client = anidb.Client()

    start = time.time()
    pong = client.ping()
    end = time.time()

    if pong:
        click.echo('{} ms'.format(round((end - start) * 1000)), err=True)
    else:
        click.echo('AniDB API server is unavailable', err=True)

    ctx.exit(not pong)


def mylistadd_file_params(file):
    return file, ed2k.file_ed2k(file), os.path.getsize(file)


@click.command()
@click.option('--ping', is_flag=True, callback=ping, is_eager=True,
              expose_value=False, help='Test connection to AniDB API server.')
@click.option('-u', '--username', prompt=True, envvar='USERNAME')
@click.option('-p', '--password', prompt=True, hide_input=True)
@click.option('-w', '--watched', is_flag=True, default=False,
              help='Mark files as watched.')
@click.option('-W', '--view-date', type=UtcDate(), default='now',
              help='Set viewdate to certain date. Implies -w/--watched.')
@click.option('-d', '--deleted', is_flag=True, default=False,
              help='Set file state to deleted.')
@click.option('-e', '--edit', is_flag=True, default=False,
              help='Set edit flag to true.')
@click.option('-j', '--jobs', default=None,
              help='Number of adding processes. Default is CPU count.')
@click.argument('files', nargs=-1,
                type=click.Path(exists=True, dir_okay=False))
def cli(username, password, watched, view_date, deleted, edit, jobs, files):
    """AniDB client for adding files to mylist."""
    client = anidb.Client()
    try:
        client.auth(username, password)
    except anidb.ClientError as e:
        raise click.ClickException(e) from e

    mp_pool = multiprocessing.Pool(jobs)

    file_params = mp_pool.imap(mylistadd_file_params, files)
    for file, file_ed2k, file_size in file_params:
        try:
            result = client.call('MYLISTADD', {
                'ed2k': file_ed2k,
                'size': file_size,
                'state': 3 if deleted else 1,  # 1 = internal storage (hdd)
                'viewed': int(watched),
                'viewdate': view_date,  # field will be disregarded if viewed=0
                'edit': int(edit),
            })

            if result.code in {210, 310, 311}:
                status = click.style(' OK ', fg='green')
            else:
                status = click.style('FAIL', fg='red')

            click.echo('[{}] {} {}'.format(status, result.message,
                                           click.format_filename(file)))
        except anidb.AnidbError as e:
            click.echo('ERROR {}'.format(str(e)), err=True)

    mp_pool.close()
    mp_pool.join()


def main():
    # pylint: disable=unexpected-keyword-arg,no-value-for-parameter
    cli(help_option_names=['-h', '--help'],
        auto_envvar_prefix='YUMEMI')


if __name__ == '__main__':
    main()
