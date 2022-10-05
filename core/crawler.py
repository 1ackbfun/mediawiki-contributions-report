import requests
import json
import csv
from .utils import Utils


class MediaWikiContributionReporter:

    @staticmethod
    def _query_api(url: str) -> str | None:
        response = requests.get(url)
        data = None
        if (response.status_code == 200):
            data = json.loads(response.text)
        return data

    def __init__(self, wiki_api) -> None:
        self.api_url = wiki_api
        self.cache = None

    def query(self, params: dict = {}) -> list:
        self.start = Utils.utc_to_cst(params['ucstart'])
        self.end = Utils.utc_to_cst(params['ucend'])
        url = self.api_url + '?origin=*'
        for key in params:
            url += f'&{key}={params[key]}'
        temp_list = []
        page_url = url
        while True:
            print(f' [INFO] 尝试请求接口 {page_url}')
            res = self._query_api(page_url)
            if res is None:
                print(f' [WARN] 请求接口失败 {page_url}')
                break
            else:
                temp_list.extend(res['query']['usercontribs'])
                if 'continue' in res:
                    page_url = url + '&uccontinue=' + \
                        res['continue']['uccontinue']
                else:
                    break
        self.cache = []
        for item in temp_list:
            if not item['title'].startswith('文件:') \
                    and not item['title'].startswith('用户:'):
                del item['ns']
                item['timestamp'] = Utils.utc_to_cst(item['timestamp'])
                self.cache.append(item)
        return self.cache

    def export_details(self, file_path: str) -> bool:
        if not self.cache:
            return False
        temp = []
        size_count = 0
        for row in self.cache:
            size_count += abs(row['sizediff'])
            temp.append([row['timestamp'], row['title'], row['sizediff']])
        with open(file_path, 'w', encoding='UTF-8-SIG', newline='') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(
                ['起始时间', self.start, '',
                 '截止时间', self.end, '',
                 '统计时间', Utils.now()])
            csv_writer.writerow(
                ['编辑次数', len(self.cache), '',
                 '总计字节数', size_count, '',
                 '理论奖励', '算法未知'])
            csv_writer.writerow([''])
            csv_writer.writerow(
                ['编辑时间', '页面标题', '变动大小'])
            for row in temp:
                csv_writer.writerow(row)
        print(f' [INFO] 已经导出到 {file_path}')
        return True

    def get_index(self) -> set:
        temp = []
        for item in self.cache:
            if not item['title'].startswith('文件:'):
                temp.append(item['title'])
        return set(temp)

    def export_indexes(self, file_path, separator='\n') -> bool:
        if not self.cache:
            return False
        with open(file_path, 'w', encoding='UTF-8') as f:
            f.write(separator.join(self.get_index()))
        print(f' [INFO] 已经导出到 {file_path}')
        return True


def main() -> None:
    CR = MediaWikiContributionReporter('https://wiki.sstmlt.com/api.php')
    Utils.Config['ucstart'] = '2022-09-27T00:00:00Z'
    Utils.Config['ucend'] = '2022-10-04T00:00:00Z'
    CR.query(Utils.Config)
    CR.export_details(r'[Test] 详细数据.csv')
    CR.export_indexes(r'[Test] 汇总清单.txt')
    return


if __name__ == '__main__':
    main()
