import os

from terminaltables import AsciiTable
import click as click
import humanize as humanize
from halo import Halo

data = []
table_header = ['file', 'size']


def iterate_route(route):
    for root, subdirectories, files in os.walk(route):
        iterate_directories(route, subdirectories)
        iterate_files(route, files)


def iterate_directories(root, directories):
    for directory in directories:
        subdirectory = os.path.join(root, directory)
        iterate_route(subdirectory)


def iterate_files(root, files):
    for file in files:
        file_path = os.path.join(root, file)

        try:
            size = os.path.getsize(file_path)
        except FileNotFoundError:
            continue

        data.append([file_path, size])


def apply_file_size_format(apply_format):
    index = 0
    for file, size in data:
        data[index][1] = file_size_format(apply_format, size)
        index += 1


def set_default_path():
    return os.path.abspath(os.sep)


def file_size_format(format, filesize):
    if format:
        return humanize.naturalsize(filesize)
    else:
        return filesize


def sort_results():
    data.sort(key=sort_by_size)
    data.reverse()


def sort_by_size(file):
    return file[1]


def check_path(ctx, param, value):
    if not os.path.exists(value):
        raise click.BadParameter("path should exist")

    return value

@click.command
@click.option('-p', '--path', help='Initial path to scan', default=lambda: set_default_path(), callback=check_path)
@click.option('-f', '--format', help='Show the file size in human readable format', is_flag=True)
@click.option('-q', '--quantity', help='Number of files to show', default=1, type=int)
def scan(path, format, quantity):
    # TODO: Verbose
    # TODO: Threads
    spinner = Halo(text='Loading', spinner='dots')
    spinner.start()
    iterate_route(path)
    spinner.stop()
    sort_results()
    apply_file_size_format(format)
    table = AsciiTable([table_header] + data[0:quantity])
    print(table.table)


if __name__ == "__main__":
    scan()
