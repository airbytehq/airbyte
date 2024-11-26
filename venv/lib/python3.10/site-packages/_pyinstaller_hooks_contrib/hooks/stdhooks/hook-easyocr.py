from PyInstaller.utils.hooks import collect_data_files, get_hook_config

# Recognition backends are imported with `importlib.import_module()`.
hiddenimports = ['easyocr.model.vgg_model', 'easyocr.model.model']


def hook(hook_api):
    lang_codes = get_hook_config(hook_api, 'easyocr', 'lang_codes')
    if not lang_codes:
        lang_codes = ['*']

    extra_datas = list()
    extra_datas += collect_data_files('easyocr', include_py_files=False, subdir='character',
                                      includes=[f'{lang_code}_char.txt' for lang_code in lang_codes])
    extra_datas += collect_data_files('easyocr', include_py_files=False, subdir='dict',
                                      includes=[f'{lang_code}.txt' for lang_code in lang_codes])

    hook_api.add_datas(extra_datas)
