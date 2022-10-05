import sys
import os
import datetime
import json


class Utils:
    API_URL = 'https://wiki.sstmlt.com/api.php'
    Config = {
        'action': 'query',
        'format': 'json',
        'list': 'usercontribs',
        'ucuser': '攸萨',
        'ucprop': 'ids|title|timestamp|comment|sizediff',
        'uclimit': 500,
        'ucdir': 'newer',
    }
    Position = (None, None)

    @staticmethod
    def get_config_path() -> str:
        # pwd = os.path.dirname(os.path.realpath(sys.argv[0]))
        pwd = os.path.dirname(os.path.realpath(sys.executable))
        return pwd + r'\config.json'

    @staticmethod
    def save_config() -> bool:
        print('[DEBUG] 已保存配置')
        with open(Utils.get_config_path(), 'w', encoding='UTF-8') as f:
            f.write(json.dumps({
                'API': Utils.API_URL,
                'Params': Utils.Config,
                'Position': list(Utils.Position),
            }))
        return False

    @staticmethod
    def load_config() -> bool:
        print('[DEBUG] 尝试加载配置')
        try:
            with open(Utils.get_config_path(), 'r', encoding='UTF-8') as f:
                conf = json.load(f)
                Utils.API_URL = conf['API']
                Utils.Config = conf['Params']
                Utils.Position = tuple(conf['Position'])
                print(f'[DEBUG] 加载配置文件成功 {Utils.Config["ucuser"]}')
        except Exception as e:
            print(f'[ERROR] Exception: {e}')
            Utils.save_config()
            print('[DEBUG] 加载配置文件失败 已重新生成')
            return False
        return True

    @staticmethod
    def now(format: str = '%Y-%m-%d %H:%M:%S') -> str:
        if format == 'TZ':
            current = datetime.datetime.strftime(
                datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            return Utils.cst_to_utc(current)
        else:
            return datetime.datetime.strftime(datetime.datetime.now(), format)

    @staticmethod
    def utc_to_cst(utc_time_str: str) -> str:
        utc_time = datetime.datetime.strptime(
            utc_time_str, '%Y-%m-%dT%H:%M:%SZ')
        cst_time = utc_time + datetime.timedelta(hours=8)
        return datetime.datetime.strftime(
            cst_time, '%Y-%m-%d %H:%M:%S')

    @staticmethod
    def cst_to_utc(cst_time_str: str) -> str:
        cst_time = datetime.datetime.strptime(
            cst_time_str, '%Y-%m-%d %H:%M:%S')
        utc_time = cst_time - datetime.timedelta(hours=8)
        return datetime.datetime.strftime(
            utc_time, '%Y-%m-%dT%H:%M:%SZ')

    @staticmethod
    def only_date(time_str: str) -> str:
        return time_str[5:10].replace('-', '.')


if __name__ == '__main__':
    print(Utils.utc_to_cst('2022-09-04T00:00:00Z'))
    print(Utils.cst_to_utc(Utils.now()))
    print(Utils.utc_to_cst(Utils.cst_to_utc(Utils.now())))
    print(Utils.now())
