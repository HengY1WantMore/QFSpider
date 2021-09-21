import argparse
import json
import sys
import factory
from common import *


print(banner)
print('Source on GitHub: https://github.com/hengyi666/Exhausted-spider\nAuthor: Hengyi')
parser = argparse.ArgumentParser(
    description='This is a tool for searching keywords to find specified urls'
)
parser.add_argument(
    '-k',
    '--key',
    required=True,
    type=str,
    help='Keywords to be present in the title'
)
parser.add_argument(
    '-w',
    '--want',
    required=False,
    type=str,
    help='Keywords should exist in the body content'
)
parser.add_argument(
    '-b',
    '--batch',
    required=False,
    type=str,
    help='Specify a JSON file to perform batch check-in. See README.md for details.'
)
parser.add_argument(
    '-s',
    '--pages',
    required=False,
    default=3,
    type=int,
    help='The default browser filters pages.'
)
parser.add_argument(
    '-r',
    '--record',
    required=False,
    default='./record/record.json',
    type=str,
    help='Write record to the specified path.'
)
parser.add_argument(
    '-t',
    '--thread',
    required=False,
    default=3,
    type=int,
    help='Number of threads for multithreading. Default is 3.'
)
args = parser.parse_args()

# 检测环境变量
key = os.getenv('chromedriver', 'null')
if key == 'null':
    print('- Warning!!!')
    print('- The Chromedriver Environment does not exist!')
    flag = input('Are U sure to continue, if Yes, push 1:')
    if flag != '1':
        print('- GoodBye')
        sys.exit(0)
else:
    print('- Congratulations. The Chromedriver Environment variables have been detected')


# 检测是否存在文件夹
path = '/'.join(args.record.split('/')[:-1])
if not os.path.exists(path):
    print('- No Record folder was detected')
    print(f'- The Record folder will be created at {path}')
    os.mkdir(path)

# 获取名单
batch_flag = False
new_list = []
if args.batch:
    for x in json.load(open(args.batch, 'r', encoding='utf-8')):
        new_dic = dict()
        for k, v in list(x.items()):
            if k == 'key':
                batch_flag = True
                new_dic[k] = v
        new_list.append(new_dic)

# 至少存在标题关键词或者内容关键词
if args.batch and not batch_flag:
    print('- Sorry, Application Error.')
    print('- Reason: At least one title keyword exists.')
    sys.exit(0)

# 针对堆项目
if args.batch:
    print('- Separate Settings for --key or --want will not take effect')
    print('- Enter the multithreading task area')
    print(f'- The number of open threads is {args.thread}')
    if args.thread > 8 or args.thread < 0:
        print(f'- Sorry, The program does not support the set number of threads.')
        sys.exit(0)
    elif args.thread >= 5:
        print('- Easter egg: Oh! You have a computer that works so well.')
        print(f'- Otherwise, check whether the performance meets the standard.')
    else:
        factory.main(new_list, args.thread, args.record, args.pages, args.open, 1)
        print('- Multithreading task completed')
        print(f"- Please go to the {args.record} to view the results")
        sys.exit(0)

# 针对单一任务
search_key = str(args.key).split(',')
if args.want:
    search_want = str(args.want).split(',')
else:
    search_want = ''
print("- Start working on a single task")
factory.main([search_key, search_want], 1, args.record, args.pages, 0)
print('- Mission Over.')
print(f"- Please go to the {args.record} to view the results")
sys.exit(0)

