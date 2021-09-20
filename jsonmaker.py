import argparse
import json
import os
from common import banner
from database import *
from config import *

print(banner)
print('Source on GitHub: https://github.com/hengyi666/QFSpider\nAuthor: Hengyi')
parser = argparse.ArgumentParser(
    description='Construct A Json File Through Connecting The Database'
)
parser.add_argument(
    '-q',
    '--query',
    required=True,
    type=str,
    help='The Query for Mysql Database.'
)
parser.add_argument(
    '-t',
    '--type',
    required=True,
    type=str,
    help='The Type Want Record.'
)
parser.add_argument(
    '--start',
    required=False,
    type=int,
    help=f'The starting number.'
)
parser.add_argument(
    '--end',
    required=False,
    type=int,
    help=f'The ending number.'
)
args = parser.parse_args()

if Work_Json_file == '':
    print(f'- Please Setting the Json Working Path at config.py')
    sys.exit(0)

if args.type != 'key' and args.type != 'want':
    print(f'- No type is supported.')
    sys.exit(0)

con = db(Mysql_Host, Mysql_UserName, Mysql_Password, Mysql_DbName, Mysql_Port, Mysql_Charset)
all_info = con.get_all(args.query)
count = len(all_info)
print(f'- {count} pieces of data are retrieved.')
if args.start and not args.end:
    info = all_info[args.start:]
elif not args.start and args.end:
    info = all_info[:args.end]
elif args.start and args.end:
    info = all_info[args.start:args.end]
else:
    info = all_info
final_num = len(info)
print(f'- After cutting the data, the final number of messages is {final_num}.')

info_list = list(map(lambda x: x[0], info))

if not os.path.exists(Work_Json_file):
    print(f'- The {Work_Json_file} File will be created')
    final_list = []
    for each in info_list:
        maker = dict()
        key = dict(enumerate([each]))
        maker[args.type] = key
        final_list.append(maker)
    with open(Work_Json_file, 'w+', encoding="utf-8") as file_obj:
        json.dump(final_list, file_obj, ensure_ascii=False)
    print(f'- Please go to {Work_Json_file} to view the result')
else:
    print(f'- The file {Work_Json_file} already exists and is about to be added new {args.type} content')
    info = json.load(open(Work_Json_file, 'r', encoding='utf-8'))
    final_list = []
    for index in range(len(info)):
        x = info[index]
        if args.type in x.keys():
            num = len(x[args.type])
            x[args.type][str(num)] = info_list[index]
            final_list.append(x)
        else:
            key = dict(enumerate([info_list[index]]))
            x[args.type] = key
            final_list.append(x)
    with open(Work_Json_file, 'w+', encoding="utf-8") as file_obj:
        json.dump(final_list, file_obj, ensure_ascii=False)
    print(f'- The new {args.type} has added successfully.')

print('- JsonMaker Woke has been done!')

