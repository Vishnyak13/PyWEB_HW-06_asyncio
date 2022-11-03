import argparse
import asyncio
from time import time
from aiopath import AsyncPath
from aioshutil import copyfile, rmtree
import logging
from normalize import normalize

parser = argparse.ArgumentParser(description='Sorting folder')
parser.add_argument("--source", "-s", help="Path to trash folder for scan", required=True)
parser.add_argument("--output", "-o", help="Path to sorted folder by file extension", default="sort_dist")

args = vars(parser.parse_args())

source = args.get("source")
output = args.get("output")

output_folder = AsyncPath(output)


async def scan_folder(path: AsyncPath) -> None:
    async for el in path.iterdir():
        if await el.is_dir():
            await scan_folder(el)
        else:
            await copy_file(el)


async def copy_file(file: AsyncPath) -> None:
    ext = file.suffix.casefold()
    if ext in ['.jpg', '.png', '.jpeg', '.bmp', '.gif', 'svg']:
        new_path = output_folder / 'images' / ext[1:].upper()
    elif ext in ['.mp3', '.wav', '.ogg', '.flac', '.aac', '.wma', '.m4a']:
        new_path = output_folder / 'audio' / ext[1:].upper()
    elif ext in ['.avi', '.mpg', '.mpeg', '.mkv', '.mov', '.flv', '.wmv', '.mp4', '.webm', '.mp4']:
        new_path = output_folder / 'video' / ext[1:].upper()
    elif ext in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', '.txt', '.rtf', '.csv']:
        new_path = output_folder / 'documents' / ext[1:].upper()
    elif ext in ['.zip', '.tag', '.gz']:
        new_path = output_folder / 'archives' / ext[1:].upper()
    else:
        new_path = output_folder / 'other'
    try:
        await new_path.mkdir(parents=True, exist_ok=True)
        await copyfile(file, new_path / normalize(file.name))
    except OSError as err:
        print(f"Can't copy file {file.name}. Error: {err}")


if __name__ == '__main__':
    start = time()
    asyncio.run(scan_folder(AsyncPath(source)))
    print(f'Sorting folder complete in {time() - start} seconds')
    print("Do you want to delete the source folder? (y/n)")
    if input() == "y":
        asyncio.run(rmtree(AsyncPath(source)))
        print("Source folder deleted successfully")
    print('Goodbye!')
