from PyInstaller.utils.hooks import collect_data_files

# Get the cacert.pem
datas = collect_data_files('certifi')
