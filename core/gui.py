from .crawler import MediaWikiContributionReporter
from .utils import Utils
import PySimpleGUIWx as gui


def make_window() -> None:
    layout = [
        [gui.Text("用户名"), gui.Input(
            Utils.Config['ucuser'], size=(20, 1), key='-USERNAME-')],
        [gui.Text("起始日期"), gui.Input(
            Utils.now('%Y-%m-01'), size=(10, 1), key='-START TIME-'),
         gui.Text("结束日期"), gui.Input(size=(10, 1), key='-END TIME-'),
         gui.Button('获取数据', key='-UPDATE-')],
        [gui.Text(size=(40, 1), key='-OUTPUT-')],
        [gui.Button('导出详细数据', key='-EXPORT DETAIL CSV-'),
         gui.Button('导出汇总清单', key='-EXPORT INDEX TXT-')],
        [gui.Text("Version 0.1.1", size=(30, 1),), gui.Text("for 勤奋的攸萨")]
    ]
    window = gui.Window('Wiki 贡献统计', layout,
                        location=Utils.Position,
                        resizable=False)  # 需要 PySimpleGUI 而不是 PySimpleGUIWx
    return window


def main() -> None:
    Utils.load_config()
    CR = MediaWikiContributionReporter(Utils.API_URL)

    window = make_window()

    # window['-USERNAME-'].update(default_text=)
    # window['-START TIME-'].update('123')

    while True:
        event, values = window.read()
        if event in ('Exit', 'Quit', gui.WINDOW_CLOSED):
            Utils.save_config()
            break
        elif event == '-UPDATE-':
            if values['-USERNAME-']:
                Utils.Config['ucuser'] = values['-USERNAME-']
                Utils.Position = window.current_location()
                Utils.save_config()
                if values['-START TIME-']:
                    Utils.Config['ucstart'] = f'{values["-START TIME-"]}T00:00:00Z'
                    if values['-END TIME-']:
                        Utils.Config['ucend'] = f'{values["-END TIME-"]}T00:00:00Z'
                    else:
                        Utils.Config['ucend'] = Utils.cst_to_utc(Utils.now())
                    window['-OUTPUT-'].update('', text_color='white')
                    window['-OUTPUT-'].update('请求数据中...')
                    CR.query(Utils.Config)
                    if CR.cache is not None and len(CR.cache) > 0:
                        window['-OUTPUT-'].update('', text_color='green')
                        window['-OUTPUT-'].update('获取数据成功')
                    else:
                        window['-OUTPUT-'].update('', text_color='red')
                        window['-OUTPUT-'].update(
                            '获取数据失败 请确认该用户是否存在 以及时间格式是否正确')
                else:
                    window['-OUTPUT-'].update('', text_color='yellow')
                    window['-OUTPUT-'].update('请先指定日期')
            else:
                window['-OUTPUT-'].update('', text_color='yellow')
                window['-OUTPUT-'].update('请先输入用户名')
        elif event == '-EXPORT DETAIL CSV-':
            year = CR.start[:4]
            period = f'{Utils.only_date(CR.start)}-{Utils.only_date(CR.end)}'
            csv_path = f'[{year}] 详细数据 {Utils.Config["ucuser"]} {period} ({len(CR.cache)}次编辑).csv'
            if CR.export_details(csv_path):
                window['-OUTPUT-'].update('', text_color='green')
                window['-OUTPUT-'].update(f'已导出 {csv_path}')
            else:
                window['-OUTPUT-'].update('', text_color='yellow')
                window['-OUTPUT-'].update('请先获取数据')
        elif event == '-EXPORT INDEX TXT-':
            year = CR.start[:4]
            period = f'{Utils.only_date(CR.start)}-{Utils.only_date(CR.end)}'
            txt_path = f'[{year}] 汇总清单 {Utils.Config["ucuser"]} {period}.txt'
            if CR.export_indexes(txt_path):
                window['-OUTPUT-'].update('', text_color='green')
                window['-OUTPUT-'].update(f'已导出 {txt_path}')
            else:
                window['-OUTPUT-'].update('', text_color='yellow')
                window['-OUTPUT-'].update('请先获取数据')

    window.close()

    return


if __name__ == '__main__':
    main()
    exit(0)
