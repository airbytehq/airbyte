# ------------------------------------------------------------------
# Copyright (c) 2020 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

import os
from pathlib import Path

import pytest

from PyInstaller.compat import is_darwin, is_linux, is_py39, is_win
from PyInstaller.utils.hooks import is_module_satisfies, can_import_module, get_module_attribute
from PyInstaller.utils.tests import importorskip, requires, xfail


@importorskip('fiona')
def test_fiona(pyi_builder):
    pyi_builder.test_source(
        '''
        import fiona
        '''
    )


@importorskip('fiona')
def test_fiona_transform(pyi_builder):
    # Test that fiona in frozen application has access to its projections database. If projection data is unavailable,
    # the transform becomes an identity transform.
    pyi_builder.test_source(
        """
        from fiona.transform import transform_geom
        from fiona.crs import from_epsg

        eiffel_tower = {
            'type': 'Point',
            'coordinates': (2.294694, 48.858093),
        }

        crs_source = from_epsg(4326)  # WGS84
        crs_target = from_epsg(25831)  # ETRS89 / UTM zone 31N

        transformed = transform_geom(crs_source, crs_target, eiffel_tower)
        print(f"Transformed point: {transformed}")

        # Expected coordinates: obtained by manually running this program unfrozen
        EXPECTED_COORDINATES = (448265.9146792292, 5411920.651338793)
        EPS = 1e-6

        delta = [abs(value - expected) for value, expected in zip(transformed["coordinates"], EXPECTED_COORDINATES)]
        print(f"Delta: {delta}")
        assert all([value < EPS for value in delta]), f"Delta {delta} exceeds threshold!"
        """
    )


@importorskip('jinxed')
def test_jinxed(pyi_builder):
    pyi_builder.test_source(
        '''
        import jinxed
        jinxed.setupterm('xterm')
        assert jinxed._terminal.TERM.terminfo is jinxed.terminfo.xterm
        '''
    )


@importorskip("geopandas")
def test_geopandas(pyi_builder):
    pyi_builder.test_source(
        '''
        import geopandas
        '''
    )


@importorskip('trimesh')
def test_trimesh(pyi_builder):
    pyi_builder.test_source(
        """
        import trimesh
        """
    )


@importorskip('apscheduler')
def test_apscheduler(pyi_builder):
    pyi_builder.test_source(
        """
        import apscheduler
        import pytz
        import asyncio
        import random
        import datetime as dt
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.interval import IntervalTrigger
        loop = asyncio.get_event_loop()
        async def test_function(data=0):
            print(dt.datetime.now(), random.randint(0, 100))
        test_scheduler = AsyncIOScheduler()
        test_scheduler.add_job(
            test_function,
            id="TestJob",
            trigger=IntervalTrigger(
                seconds=1,
                start_date=dt.datetime.now(tz=pytz.UTC)
            )
        )
        test_scheduler.start()
        loop.run_until_complete(asyncio.sleep(5))
    """
    )


@importorskip('boto')
@xfail(reason='boto does not fully support Python 3')
def test_boto(pyi_builder):
    pyi_builder.test_script('pyi_lib_boto.py')


@xfail(reason='Issue #1844.')
@importorskip('boto3')
def test_boto3(pyi_builder):
    pyi_builder.test_source(
        """
        import boto3
        session = boto3.Session(region_name='us-west-2')

        # verify all clients
        for service in session.get_available_services():
            session.client(service)

        # verify all resources
        for resource in session.get_available_resources():
            session.resource(resource)
        """)


@xfail(reason='Issue #1844.')
@importorskip('botocore')
def test_botocore(pyi_builder):
    pyi_builder.test_source(
        """
        import botocore
        from botocore.session import Session
        session = Session()
        # verify all services
        for service in session.get_available_services():
            session.create_client(service, region_name='us-west-2')
        """)


@xfail(is_darwin, reason='Issue #1895.')
@importorskip('enchant')
def test_enchant(pyi_builder):
    pyi_builder.test_script('pyi_lib_enchant.py')


@importorskip('zmq')
def test_zmq(pyi_builder):
    pyi_builder.test_source(
        """
        import zmq
        print(zmq.__version__)
        print(zmq.zmq_version())
        # This is a problematic module and might cause some issues.
        import zmq.utils.strtypes
        """)


@importorskip('pylint')
def test_pylint(pyi_builder):
    pyi_builder.test_source(
        """
        # The following more obvious test doesn't work::
        #
        #   import pylint
        #   pylint.run_pylint()
        #
        # because pylint will exit with 32, since a valid command
        # line wasn't given. Instead, provide a valid command line below.

        from pylint.lint import Run
        Run(['-h'])
        """)


@importorskip('markdown')
def test_markdown(pyi_builder):
    # Markdown uses __import__ed extensions. Make sure these work by
    # trying to use the 'toc' extension, using both short and long format.
    pyi_builder.test_source(
        """
        import markdown
        print(markdown.markdown('testing',
            extensions=['toc']))
        print(markdown.markdown('testing',
            extensions=['markdown.extensions.toc']))
        """)


@importorskip('pylsl')
def test_pylsl(pyi_builder):
    pyi_builder.test_source(
        """
        import pylsl
        print(pylsl.version.__version__)
        """)


@importorskip('lxml')
def test_lxml_isoschematron(pyi_builder):
    pyi_builder.test_source(
        """
        # The import of this module triggers the loading of some
        # required XML files.
        from lxml import isoschematron
        """)


@importorskip('openpyxl')
def test_openpyxl(pyi_builder):
    pyi_builder.test_source(
        """
        # Test the hook to openpyxl
        from openpyxl import __version__
        """)


@importorskip('pyodbc')
def test_pyodbc(pyi_builder):
    pyi_builder.test_source(
        """
        # pyodbc is a binary Python module. On Windows when installed with easy_install
        # it is installed as zipped Python egg. This binary module is extracted
        # to PYTHON_EGG_CACHE directory. PyInstaller should find the binary there and
        # include it with frozen executable.
        import pyodbc
        """)


@importorskip('pyttsx')
def test_pyttsx(pyi_builder):
    pyi_builder.test_source(
        """
        # Basic code example from pyttsx tutorial.
        # http://packages.python.org/pyttsx/engine.html#examples
        import pyttsx
        engine = pyttsx.init()
        engine.say('Sally sells seashells by the seashore.')
        engine.say('The quick brown fox jumped over the lazy dog.')
        engine.runAndWait()
        """)


@importorskip('pyttsx3')
def test_pyttsx3(pyi_builder):
    pyi_builder.test_source("""
        import pyttsx3
        engine = pyttsx3.init()
    """)


@importorskip('pycparser')
def test_pycparser(pyi_builder):
    pyi_builder.test_script('pyi_lib_pycparser.py')


@importorskip('Crypto')
def test_pycrypto(pyi_builder):
    pyi_builder.test_source(
        """
        import binascii
        from Crypto.Cipher import AES
        BLOCK_SIZE = 16
        print('AES null encryption, block size', BLOCK_SIZE)
        # Just for testing functionality after all
        print('HEX', binascii.hexlify(
            AES.new(b"\\0" * BLOCK_SIZE, AES.MODE_ECB).encrypt(b"\\0" * BLOCK_SIZE)))
        from Crypto.PublicKey import ECC
        """)


@importorskip('Cryptodome')
def test_cryptodome(pyi_builder):
    pyi_builder.test_source(
        """
        from Cryptodome import Cipher
        from Cryptodome.PublicKey import ECC
        print('Cryptodome Cipher Module:', Cipher)
        """)


@importorskip('h5py')
def test_h5py(pyi_builder):
    pyi_builder.test_source("""
        import h5py
        """)


@importorskip('unidecode')
def test_unidecode(pyi_builder):
    pyi_builder.test_source("""
        from unidecode import unidecode

        # Unidecode should not skip non-ASCII chars if mappings for them exist.
        assert unidecode(u"kožušček") == "kozuscek"
        """)


@importorskip('pinyin')
def test_pinyin(pyi_builder):
    pyi_builder.test_source("""
        import pinyin
        """)


@importorskip('uvloop')
@pytest.mark.darwin
@pytest.mark.linux
def test_uvloop(pyi_builder):
    pyi_builder.test_source("import uvloop")


@importorskip('web3')
def test_web3(pyi_builder):
    pyi_builder.test_source("import web3")


@importorskip('phonenumbers')
def test_phonenumbers(pyi_builder):
    pyi_builder.test_source("""
        import phonenumbers

        number = '+17034820623'
        parsed_number = phonenumbers.parse(number)

        assert(parsed_number.country_code == 1)
        assert(parsed_number.national_number == 7034820623)
        """)


@importorskip('pendulum')
def test_pendulum(pyi_builder):
    pyi_builder.test_source("""
        import pendulum

        print(pendulum.now().isoformat())
        """)


@importorskip('humanize')
def test_humanize(pyi_builder):
    pyi_builder.test_source("""
        import humanize
        from datetime import timedelta

        print(humanize.naturaldelta(timedelta(seconds=125)))
        """)


@importorskip('argon2')
def test_argon2(pyi_builder):
    pyi_builder.test_source("""
        from argon2 import PasswordHasher

        ph = PasswordHasher()
        hash = ph.hash("s3kr3tp4ssw0rd")
        ph.verify(hash, "s3kr3tp4ssw0rd")
        """)


@importorskip('pytest')
def test_pytest_runner(pyi_builder):
    """
    Check if pytest runner builds correctly.
    """
    pyi_builder.test_source(
        """
        import pytest
        import sys
        sys.exit(pytest.main(['--help']))
        """)


@importorskip('eel')
def test_eel(pyi_builder):
    pyi_builder.test_source("import eel")


@importorskip('sentry_sdk')
def test_sentry(pyi_builder):
    pyi_builder.test_source(
        """
        import sentry_sdk
        sentry_sdk.init()
        """)


@importorskip('iminuit')
def test_iminuit(pyi_builder):
    pyi_builder.test_source("""
        from iminuit import Minuit
        """)


@importorskip('av')
def test_av(pyi_builder):
    pyi_builder.test_source("""
        import av
        """)


@importorskip('passlib')
@xfail(is_linux and is_py39 and not is_module_satisfies('passlib > 1.7.4'),
       reason='Passlib does not account for crypt() behavior change that '
              'was introduced in 3.9.x (python #39289).')
def test_passlib(pyi_builder):
    pyi_builder.test_source("""
        import passlib.apache
        """)


@importorskip('publicsuffix2')
def test_publicsuffix2(pyi_builder):
    pyi_builder.test_source("""
        import publicsuffix2
        publicsuffix2.PublicSuffixList()
        """)


@importorskip('pydivert')
def test_pydivert(pyi_builder):
    pyi_builder.test_source("""
        import pydivert
        pydivert.WinDivert.check_filter("inbound")
        """)


@importorskip('statsmodels')
@pytest.mark.skipif(not is_module_satisfies('statsmodels >= 0.12'),
                    reason='This has only been tested with statsmodels >= 0.12.')
def test_statsmodels(pyi_builder):
    pyi_builder.test_source("""
        import statsmodels.api as sm
        """)


@importorskip('win32ctypes')
@pytest.mark.skipif(not is_win, reason='pywin32-ctypes is supported only on Windows')
@pytest.mark.parametrize('submodule', ['win32api', 'win32cred', 'pywintypes'])
def test_pywin32ctypes(pyi_builder, submodule):
    pyi_builder.test_source("""
        from win32ctypes.pywin32 import {0}
        """.format(submodule))


@importorskip('pyproj')
@pytest.mark.skipif(not is_module_satisfies('pyproj >= 2.1.3'),
                    reason='The test supports only pyproj >= 2.1.3.')
def test_pyproj(pyi_builder):
    pyi_builder.test_source("""
        import pyproj
        tf = pyproj.Transformer.from_crs(
            7789,
            8401
        )
        result = tf.transform(
            xx=3496737.2679,
            yy=743254.4507,
            zz=5264462.9620,
            tt=2019.0
        )
        print(result)
        """)


@importorskip('pydantic')
def test_pydantic(pyi_builder):
    pyi_builder.test_source("""
        import datetime
        import pprint

        import pydantic


        class User(pydantic.BaseModel):
            id: int
            name: str = 'John Doe'
            signup_ts: datetime.datetime


        external_data = {'id': 'not an int', }
        try:
            User(**external_data)
        except pydantic.ValidationError as e:
            pprint.pprint(e.errors())
        """)


@requires('google-api-python-client >= 2.0.0')
def test_googleapiclient(pyi_builder):
    pyi_builder.test_source("""
        from googleapiclient import discovery, discovery_cache

        API_NAME = "youtube"
        API_VERSION = "v3"

        for file in os.listdir(discovery_cache.DISCOVERY_DOC_DIR): # Always up to date
            if file.startswith("youtube.v") and file.endswith(".json"):
                API_NAME, API_VERSION = file.split(".")[:2]
                break

        # developerKey can be any non-empty string
        yt = discovery.build(API_NAME, API_VERSION, developerKey=":)", static_discovery=True)
        """)


@importorskip('eth_typing')
def test_eth_typing(pyi_builder):
    pyi_builder.test_source("""
        import eth_typing
    """)


@importorskip("eth_utils")
def test_eth_utils_network(pyi_builder):
    pyi_builder.test_source("""
        import eth_utils.network
        eth_utils.network.name_from_chain_id(1)
    """)


@importorskip('plotly')
@importorskip('pandas')
def test_plotly(pyi_builder):
    pyi_builder.test_source("""
        import pandas as pd
        import plotly.express as px

        data = [(1, 1), (2, 1), (3, 5), (4, -3)]
        df = pd.DataFrame.from_records(data, columns=['col_1', 'col_2'])
        fig = px.scatter(df, x='col_1', y='col_2')
        """)


@pytest.mark.timeout(600)
@importorskip('dash')
def test_dash(pyi_builder):
    pyi_builder.test_source("""
        import dash
        import dash_core_components as dcc
        import dash_html_components as html
        from dash.dependencies import Input, Output

        app = dash.Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Input(id='input_text', type='text', placeholder='input type text'),
                html.Div(id='out-all-types'),
            ]
        )

        @app.callback(
            Output('out-all-types', 'children'),
            [Input('input_text', 'value')],
        )
        def cb_render(val):
            return val
        """)


@importorskip('dash_table')
def test_dash_table(pyi_builder):
    pyi_builder.test_source("""
        import dash
        import dash_table

        app = dash.Dash(__name__)
        app.layout = dash_table.DataTable(
            id='table',
            columns=[{'name': 'a', 'id': 'a'}, {'name': 'b', 'id': 'b'}],
            data=[{'a': 1, 'b': 2}, {'a': 3, 'b': 4}],
        )
        """)


@importorskip('dash_bootstrap_components')
def test_dash_bootstrap_components(pyi_builder):
    pyi_builder.test_source("""
        import dash
        import dash_bootstrap_components as dbc
        import dash_html_components as html

        app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
        alert = dbc.Alert([html.H4('Well done!', className='alert-heading')])
        """)


@importorskip('blspy')
def test_blspy(pyi_builder):
    pyi_builder.test_source("""
        import blspy
        """)


@importorskip('flirpy')
def test_flirpy(pyi_builder):
    pyi_builder.test_source("""
        from flirpy.camera.lepton import Lepton

        print(Lepton.find_video_device())
        """)


@importorskip('office365')
def test_office365(pyi_builder):
    pyi_builder.test_source("""
        from office365.runtime.auth.providers.saml_token_provider import SamlTokenProvider

        SamlTokenProvider._prepare_request_from_template('FederatedSAML.xml', {})
        SamlTokenProvider._prepare_request_from_template('RST2.xml', {})
        SamlTokenProvider._prepare_request_from_template('SAML.xml', {})
        """)


@importorskip('thinc')
def test_thinc(pyi_builder):
    pyi_builder.test_source("""
        from thinc.backends import numpy_ops
        """)


@importorskip('srsly')
def test_srsly(pyi_builder):
    pyi_builder.test_source("""
        import srsly
        """)


@importorskip('spacy')
def test_spacy(pyi_builder):
    pyi_builder.test_source("""
        import spacy
        """)


@importorskip('shotgun_api3')
def test_shotgun_api3(pyi_builder):
    pyi_builder.test_source("""
        import shotgun_api3
        """)


@importorskip('msoffcrypto')
def test_msoffcrypto(pyi_builder):
    pyi_builder.test_source("""
        import msoffcrypto
        """)


@importorskip('mariadb')
def test_mariadb(pyi_builder):
    pyi_builder.test_source("""
        import mariadb
        """)


@importorskip('dash_uploader')
def test_dash_uploader(pyi_builder):
    pyi_builder.test_source("""
        import dash_uploader
        """)


@importorskip('cloudscraper')
def test_cloudscraper(pyi_builder):
    pyi_builder.test_source("""
        import cloudscraper
        scraper = cloudscraper.create_scraper()
        """)


@importorskip('mnemonic')
def test_mnemonic(pyi_builder):
    pyi_builder.test_source("""
        import mnemonic
        mnemonic.Mnemonic("english")
        """)


@importorskip('pynput')
def test_pynput(pyi_builder):
    pyi_builder.test_source("""
        import pynput
        """)


@importorskip('pystray')
def test_pystray(pyi_builder):
    pyi_builder.test_source("""
        import pystray
        """)


@importorskip('rtree')
def test_rtree(pyi_builder):
    pyi_builder.test_source("""
        import rtree
        """)


@importorskip('pingouin')
def test_pingouin(pyi_builder):
    pyi_builder.test_source("""
        import pingouin
        """)


@importorskip('timezonefinder')
def test_timezonefinder(pyi_builder):
    pyi_builder.test_source("""
        from timezonefinder import TimezoneFinder
        TimezoneFinder()
        """)


@importorskip('uvicorn')
def test_uvicorn(pyi_builder):
    pyi_builder.test_source("""
        from uvicorn import lifespan, loops
        """)


@importorskip("langdetect")
def test_langdetect(pyi_builder):
    pyi_builder.test_source("""
        import langdetect
        print(langdetect.detect("this is a test"))
        """)


@importorskip("swagger_spec_validator")
def test_swagger_spec_validator(pyi_builder):
    pyi_builder.test_source("""
        from swagger_spec_validator.common import read_resource_file
        read_resource_file("schemas/v1.2/resourceListing.json")
        read_resource_file("schemas/v2.0/schema.json")
        """)


@requires('pythonnet < 3.dev')
@pytest.mark.skipif(not is_win, reason='pythonnet 2 does not support .Net Core, so its only supported by Windows')
def test_pythonnet2(pyi_builder):
    pyi_builder.test_source("""
        import clr
        """)


@requires('pythonnet >= 3.dev')
def test_pythonnet3(pyi_builder):
    pyi_builder.test_source("""
        from clr_loader import get_coreclr
        from pythonnet import set_runtime
        set_runtime(get_coreclr())  # Pick up and use any installed .NET runtime.

        import clr
        """)


if is_win:
    # This is a hack to prevent monkeypatch from interfering with PyQt5's additional PATH entries. See:
    # https://github.com/pyinstaller/pyinstaller/commit/b66c9021129e9e875ddd138a298ce542483dd6c9
    try:
        import PyQt5  # noqa: F401
    except ImportError:
        pass


@importorskip("qtmodern")
@importorskip("PyQt5")
def test_qtmodern(pyi_builder):
    pyi_builder.test_source("""
        import sys
        from PyQt5 import QtWidgets
        import qtmodern.styles
        import qtmodern.windows

        app = QtWidgets.QApplication(sys.argv)
        window = QtWidgets.QWidget()
        qtmodern.styles.dark(app)
        modern_window = qtmodern.windows.ModernWindow(window)
        modern_window.show()
        """)


@importorskip("platformdirs")
def test_platformdirs(pyi_builder):
    pyi_builder.test_source("""
        import platformdirs
        platformdirs.user_data_dir("FooApp", "Mr Foo")
        """)


@importorskip("websockets")
def test_websockets(pyi_builder):
    pyi_builder.test_source("import websockets")


@importorskip("tableauhyperapi")
def test_tableauhyperapi(pyi_builder):
    pyi_builder.test_source("""
        import tableauhyperapi
        """)


@importorskip("pymssql")
def test_pymssql(pyi_builder):
    pyi_builder.test_source("""
        import pymssql
        """)


@importorskip("branca")
def test_branca(pyi_builder):
    pyi_builder.test_source("""
        import branca
        """)


@importorskip("folium")
def test_folium(pyi_builder):
    pyi_builder.test_source("""
        import folium
        m = folium.Map(location=[0, 0], zoom_start=5)
        """)


@importorskip("metpy")
def test_metpy(pyi_builder):
    # Import metpy.plots, which triggers search for colortables data.
    pyi_builder.test_source("""
        import metpy.plots
        """)


@importorskip("pyvjoy")
def test_pyvjoy(pyi_builder):
    pyi_builder.test_source("""
        import pyvjoy
        """)


@importorskip("adbutils")
def test_adbutils(pyi_builder):
    # adbutils 0.15.0 renamed adbutils._utils.get_adb_exe() to adb_path()
    if is_module_satisfies("adbutils >= 0.15.0"):
        pyi_builder.test_source("""
            from adbutils._utils import adb_path; adb_path()
            """)
    else:
        pyi_builder.test_source("""
            from adbutils._utils import get_adb_exe; get_adb_exe()
            """)


@importorskip("pymediainfo")
def test_pymediainfo(pyi_builder):
    pyi_builder.test_source("""
        from pymediainfo import MediaInfo
        MediaInfo._get_library()  # Trigger search for shared library.
        """)


@importorskip("sacremoses")
def test_sacremoses(pyi_builder):
    pyi_builder.test_source("""
        import sacremoses
        """)


@importorskip("pypeteer")
def test_pypeteer(pyi_builder):
    pyi_builder.test_source("""
        import pypeteer
        print(pypeteer.version)
        """)


@importorskip("tzdata")
@pytest.mark.skipif(not is_py39 and not can_import_module('importlib_resources'),
                    reason='importlib_resources is required on python < 3.9.')
def test_tzdata(pyi_builder):
    pyi_builder.test_source("""
        import tzdata.zoneinfo  # hiddenimport

        try:
            import importlib.resources as importlib_resources
        except ImportError:
            import importlib_resources

        # This emulates time-zone data retrieval from tzdata, as peformed by
        # zoneinfo / backports.zoneinfo
        zone_name = "Europe/Ljubljana"

        components = zone_name.split("/")
        package_name = ".".join(["tzdata.zoneinfo"] + components[:-1])
        resource_name = components[-1]

        with importlib_resources.open_binary(package_name, resource_name) as fp:
            data = fp.read()

        print(data)
        """)


@importorskip("backports.zoneinfo")
@pytest.mark.skipif(is_win and not can_import_module('tzdata'),
                    reason='On Windows, backports.zoneinfo requires tzdata.')
def test_backports_zoneinfo(pyi_builder):
    pyi_builder.test_source("""
        from backports import zoneinfo
        tz = zoneinfo.ZoneInfo("Europe/Ljubljana")
        print(tz)
        """)


@importorskip("zoneinfo")
@pytest.mark.skipif(is_win and not can_import_module('tzdata'),
                    reason='On Windows, zoneinfo requires tzdata.')
def test_zoneinfo(pyi_builder):
    pyi_builder.test_source("""
        import zoneinfo
        tz = zoneinfo.ZoneInfo("Europe/Ljubljana")
        print(tz)
        """)


@importorskip("panel")
def test_panel(pyi_builder):
    pyi_builder.test_source("""
        import panel

        # Load the Ace extension to trigger lazy-loading of model
        panel.extension("ace")
        """)


@importorskip("pyviz_comms")
def test_pyviz_comms(pyi_builder):
    pyi_builder.test_source("""
        import pyviz_comms
        """)


@importorskip("pyphen")
def test_pyphen(pyi_builder):
    pyi_builder.test_source("""
        import pyphen
        """)


@importorskip("pandas")
@importorskip("plotly")
@importorskip("kaleido")
def test_kaleido(pyi_builder):
    pyi_builder.test_source("""
        import plotly.express as px
        fig = px.scatter(px.data.iris(), x="sepal_length", y="sepal_width", color="species")
        fig.write_image("figure.png", engine="kaleido")
        """)


@pytest.mark.skipif(is_win,
                    reason='On Windows, Cairo dependencies cannot be installed using Chocolatey.')
@importorskip("cairocffi")
def test_cairocffi(pyi_builder):
    pyi_builder.test_source("""
        import cairocffi
        """)


@pytest.mark.skipif(is_win,
                    reason='On Windows, Cairo dependencies cannot be installed using Chocolatey.')
@importorskip("cairosvg")
def test_cairosvg(pyi_builder):
    pyi_builder.test_source("""
        import cairosvg
        """)


@importorskip("ffpyplayer")
def test_ffpyplayer(pyi_builder):
    pyi_builder.test_source("""
        import ffpyplayer.player
        """)


@importorskip("cv2")
def test_cv2(pyi_builder):
    pyi_builder.test_source("""
        import cv2
        """)


# Requires OpenCV with enabled HighGUI
@importorskip("cv2")
def test_cv2_highgui(pyi_builder):
    from PyInstaller import isolated

    @isolated.decorate
    def _get_cv2_highgui_backend():
        import re
        import cv2

        # Find `GUI: <type>` line in OpenCV build information dump. This is available only in recent OpenCV versions;
        # in earlier versions, we would need to parse all subsequent backend entries, which is out of our scope here.
        pattern = re.compile(r'$\s*GUI\s*:\s*(?P<gui>\S+)\s*^', re.MULTILINE)
        info = cv2.getBuildInformation()
        m = pattern.search(info)
        if not m:
            return None

        return m.group('gui')

    has_gui = True
    backend = _get_cv2_highgui_backend()
    if backend is None:
        # We could not determine the backend from OpenCV information; fall back to the dist name
        if is_module_satisfies('opencv-python-headless'):
            has_gui = False
    elif backend == "NONE":
        has_gui = False

    if not has_gui:
        pytest.skip("OpenCV has no GUI support.")

    pyi_builder.test_source("""
        import cv2
        import numpy as np

        img = np.zeros((64, 64), dtype='uint8')
        cv2.imshow("Test", img)
        cv2.waitKey(1000)  # Wait a second
        """)


@importorskip("twisted")
def test_twisted_default_reactor(pyi_builder):
    pyi_builder.test_source("""
        from twisted.internet import reactor
        assert callable(reactor.listenTCP)
        """)


@importorskip("twisted")
def test_twisted_custom_reactor(pyi_builder):
    pyi_builder.test_source("""
        import sys
        if sys.platform.startswith("win") and sys.version_info >= (3,7):
            import asyncio
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        from twisted.internet import asyncioreactor
        asyncioreactor.install()
        from twisted.internet import reactor
        assert callable(reactor.listenTCP)
        """)


@importorskip("pygraphviz")
def test_pygraphviz_bundled_programs(pyi_builder):
    # Test that the frozen application is using collected graphviz executables instead of system-installed ones.
    pyi_builder.test_source("""
        import sys
        import os
        import pygraphviz

        bundle_dir = os.path.normpath(sys._MEIPASS)
        dot_path = os.path.normpath(pygraphviz.AGraph()._get_prog('dot'))

        assert os.path.commonprefix([dot_path, bundle_dir]) == bundle_dir, \
            f"Invalid program path: {dot_path}!"
        """)


@importorskip("pypsexec")
def test_pypsexec(pyi_builder):
    pyi_builder.test_source("""
        from pypsexec.paexec import paexec_out_stream
        next(paexec_out_stream())
        """)


@importorskip("mimesis")
def test_mimesis(pyi_builder):
    pyi_builder.test_source("""
        from mimesis import Address
        Address().address()
        """)


@importorskip('orjson')
def test_orjson(pyi_builder):
    pyi_builder.test_source("""
        import orjson
        """)


@importorskip('altair')
def test_altair(pyi_builder):
    pyi_builder.test_source("""
        import altair
        """)


@importorskip('fabric')
def test_fabric(pyi_builder):
    pyi_builder.test_source("""
        import fabric
        """)


@importorskip('cassandra')
def test_cassandra(pyi_builder):
    pyi_builder.test_source("""
        import cassandra
        """)


@importorskip('gitlab')
def test_gitlab(pyi_builder):
    pyi_builder.test_source("""
        import gitlab
        """)


@importorskip('graphql_query')
def test_graphql_query(pyi_builder):
    pyi_builder.test_source("""
        from graphql_query import Operation, Query
        hero = Query(name="hero", fields=["name"])
        operation = Operation(type="query", queries=[hero])
        print(operation.render())
        """)


@importorskip('shapely')
def test_shapely(pyi_builder):
    pyi_builder.test_source("""
        from shapely.geometry import Point
        patch = Point(0.0, 0.0).buffer(10.0)
        print(patch.area)
        """)


@importorskip('lark')
def test_lark(pyi_builder):
    pyi_builder.test_source("""
        import lark
        parser = lark.Lark('''
            value: "true"
            %import common.SIGNED_NUMBER''',
            start='value')
    """)


@importorskip('stdnum')
def test_stdnum_iban(pyi_builder):
    pyi_builder.test_source("""
        import stdnum.iban
    """)


@importorskip('numcodecs')
def test_numcodecs(pyi_builder):
    pyi_builder.test_source("""
        # numcodecs uses multiprocessing
        import multiprocessing
        multiprocessing.freeze_support()
        from numcodecs import Blosc
    """)


@importorskip('pypemicro')
def test_pypemicro(pyi_builder):
    pyi_builder.test_source("""
        from pypemicro import PyPemicro
        assert PyPemicro.get_pemicro_lib()
    """)


@importorskip('sounddevice')
def test_sounddevice(pyi_builder):
    pyi_builder.test_source("""
        import sounddevice
    """)


@importorskip('soundfile')
def test_soundfile(pyi_builder):
    pyi_builder.test_source("""
        import soundfile
    """)


@importorskip('limits')
def test_limits(pyi_builder):
    pyi_builder.test_source("""
        import limits
    """)


@pytest.mark.skipif(is_win,
                    reason='On Windows, Weasyprint dependencies cannot be installed using Chocolatey.')
@importorskip("weasyprint")
def test_weasyprint(pyi_builder):
    pyi_builder.test_source("""
        import weasyprint
        """)


@importorskip("great_expectations")
def test_great_expectations(pyi_builder):
    # Reproduce the error from pyinstaller/pyinstaller-hooks-contrib#445
    pyi_builder.test_source("""
        from great_expectations.render.view import view
        v = view.DefaultJinjaView()
        """)


@importorskip('pyshark')
def test_pyshark(pyi_builder):
    pyi_builder.test_source(
        """
        import pyshark
        #capture = pyshark.FileCapture('/tmp/networkpackages.cap')
        #data = [print x for x in capture]
        #print(data)
        """
    )


@importorskip('pyqtgraph')
@importorskip('PyQt5')
def test_pyqtgraph(pyi_builder):
    pyi_builder.test_source(
        """
        import pyqtgraph.graphicsItems.PlotItem
        import pyqtgraph.graphicsItems.ViewBox.ViewBoxMenu
        import pyqtgraph.imageview.ImageView
        """,
        pyi_args=['--exclude', 'PySide2', '--exclude', 'PySide6', '--exclude', 'PyQt6']
    )


@importorskip('pyqtgraph')
def test_pyqtgraph_colormap(pyi_builder):
    pyi_builder.test_source(
        """
        import pyqtgraph.colormap
        assert pyqtgraph.colormap.listMaps()
        """
    )


@importorskip('pyqtgraph')
@importorskip('PyQt5')
def test_pyqtgraph_remote_graphics_view(pyi_builder):
    pyi_builder.test_source(
        """
        import sys
        import os
        import signal

        from PyQt5 import QtCore, QtWidgets
        import pyqtgraph

        # Multiprocessing is used internally by pyqtgraph.multiprocess
        import multiprocessing
        multiprocessing.freeze_support()

        # pyqtgraph.multiprocess also uses a subprocess.Popen() to spawn its
        # sub-process, so we need to restore _MEIPASS2 to prevent the executable
        # to unpacking itself again in the subprocess.
        os.environ['_MEIPASS2'] = sys._MEIPASS

        # Create a window with remote graphics view
        app = QtWidgets.QApplication(sys.argv)
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        window = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(window)
        remote_view = pyqtgraph.widgets.RemoteGraphicsView.RemoteGraphicsView()
        layout.addWidget(remote_view)

        window.show()

        # Quit after a second
        QtCore.QTimer.singleShot(1000, app.exit)

        sys.exit(app.exec_())
        """,
        pyi_args=['--exclude', 'PySide2', '--exclude', 'PySide6', '--exclude', 'PyQt6']
    )


# Remove xfail once facebookresearch/hydra#2531 is merged.
@importorskip('hydra')
@xfail(
    is_module_satisfies('PyInstaller >= 5.8'),
    reason="uses deprecated PEP-302 functionality that was removed from PyInstaller's FrozenImporter.")
def test_hydra(pyi_builder, tmpdir):
    config_file = str((Path(__file__) / '../data/test_hydra/config.yaml').resolve(strict=True).as_posix())

    pyi_builder.test_source(
        """
        import os

        import hydra
        from omegaconf import DictConfig, OmegaConf

        config_path = os.path.join(os.path.dirname(__file__), 'conf')

        @hydra.main(config_path=config_path, config_name="config")
        def my_app(cfg):
            assert cfg.test_group.secret_string == 'secret'
            assert cfg.test_group.secret_number == 123

        if __name__ == "__main__":
            my_app()
        """,
        pyi_args=['--add-data', os.pathsep.join((config_file, 'conf'))]
    )


@importorskip('pywintypes')
def test_pywintypes(pyi_builder):
    pyi_builder.test_source("""
        import pywintypes
        """)


@importorskip('pythoncom')
def test_pythoncom(pyi_builder):
    pyi_builder.test_source("""
        import pythoncom
        """)


@importorskip('spiceypy')
def test_spiceypy(pyi_builder):
    pyi_builder.test_source("""
        import spiceypy
    """)


@importorskip('discid')
def test_discid(pyi_builder):
    pyi_builder.test_source(
        """
        # Basic import check
        import discid

        # Check that shared library is in fact collected into application bundle.
        # We expect the hook to collect it to top-level directory (sys._MEIPASS).
        import discid.libdiscid
        lib_name = discid.libdiscid._LIB_NAME

        lib_file = os.path.join(sys._MEIPASS, lib_name)
        assert os.path.isfile(lib_file), f"Shared library {lib_name} not collected to _MEIPASS!"
        """
    )


@importorskip('exchangelib')
def test_exchangelib(pyi_builder):
    pyi_builder.test_source("""
        import exchangelib
    """)


@importorskip('cftime')
def test_cftime(pyi_builder):
    pyi_builder.test_source("""
        import cftime
    """)


@importorskip('netCDF4')
def test_netcdf4(pyi_builder):
    pyi_builder.test_source("""
        import netCDF4
    """)


@importorskip('charset_normalizer')
def test_charset_normalizer(pyi_builder):
    pyi_builder.test_source("""
        import base64
        import charset_normalizer
        message = base64.b64decode(b"yUCEmYWBlIWEQIFAhJmFgZRAloZAgUCUlpmFQKKFlaKJgpOFQJeBg5KBh4U=")
        print(charset_normalizer.from_bytes(message).best())
    """)


@importorskip('cf_units')
def test_cf_units(pyi_builder):
    pyi_builder.test_source("""
        import cf_units
    """)


@importorskip('compliance_checker')
def test_compliance_checker(pyi_builder):
    # The test file - taken from the package's own test data/examples. Use an .nc file instead of .cdl one, because
    # loading the latter requires ncgen utility to be available on the system.
    pkg_path = get_module_attribute('compliance_checker', '__path__')[0]
    input_file = Path(pkg_path) / 'tests/data/bad-trajectory.nc'
    assert input_file.is_file(), f"Selected test file, {input_file!s} does not exist! Fix the test!"

    pyi_builder.test_source("""
        import os
        import json

        import compliance_checker
        import compliance_checker.runner

        input_file = sys.argv[1]

        # Load all available checker classes
        check_suite = compliance_checker.runner.CheckSuite()
        check_suite.load_all_available_checkers()

        # Run cf and adcc checks
        return_value, errors = compliance_checker.runner.ComplianceChecker.run_checker(
            input_file,
            checker_names=['cf', 'acdd'],
            verbose=False,
            criteria='normal',
            output_filename='-',
            output_format='json')

        # We do not really care about validation results, just that validation finished without raising any exceptions.
        print("Return value:", return_value)
        print("Errors occurred:", errors)
    """, app_args=[str(input_file)])


@importorskip('nbt')
def test_nbt(pyi_builder):
    pyi_builder.test_source("""
        import nbt
    """)


@importorskip('minecraft_launcher_lib')
def test_minecraft_launcher_lib(pyi_builder):
    pyi_builder.test_source(
        '''
        import minecraft_launcher_lib
        assert isinstance(minecraft_launcher_lib.utils.get_library_version(), str)
        '''
    )


@importorskip('moviepy')
def test_moviepy_editor(pyi_builder):
    # `moviepy.editor` tries to access the `moviepy.video.fx` and `moviepy.audio.fx` plugins/modules via the
    # `moviepy.video.fx.all` and `moviepy.video.fx.all` modules, which in turn programmatically import and
    # forward all corresponding submodules.
    pyi_builder.test_source("""
        import moviepy.editor
    """)


@importorskip('customtkinter')
def test_customtkinter(pyi_builder):
    pyi_builder.test_source("""
        import customtkinter
    """)


@importorskip('pylibmagic')
def test_pylibmagic(pyi_builder):
    pyi_builder.test_source("""
        import pylibmagic
        import os
        import sys

        bundle_dir = os.path.normpath(sys._MEIPASS)
        pylibmagic_data_path = f"{bundle_dir}/pylibmagic"

        files_to_assert = ["magic.mgc"]
        if sys.platform == 'darwin':
            files_to_assert.append("libmagic.1.dylib")
        elif sys.platform.startswith('linux'):
            files_to_assert.append("libmagic.so.1")

        for file in files_to_assert:
            assert os.path.isfile(f"{pylibmagic_data_path}/{file}"), \
                f"The {file} was not collected to _MEIPASS!"
    """)


@importorskip('fastparquet')
def test_fastparquet(pyi_builder):
    pyi_builder.test_source("""
        import fastparquet
    """)


@importorskip('librosa')
def test_librosa(pyi_builder):
    pyi_builder.test_source("""
        import librosa

        # Requires intervals.msgpack data file
        import librosa.core.intervals

        # Requires example files on import
        import librosa.util.files
    """)


@importorskip('librosa')
def test_librosa_util_function(pyi_builder):
    # Test that functions from `librosa.util` that use `numba` vectorization can be run in frozen application.
    pyi_builder.test_source("""
        import librosa.util
        import numpy as np

        x = np.array([1, 0, 1, 2, -1, 0, -2, 1])
        result = librosa.util.localmin(x)
        expected = np.array([False,  True, False, False,  True, False,  True, False])
        assert (result == expected).all()
    """)


@importorskip('sympy')
def test_sympy(pyi_builder):
    pyi_builder.test_source("""
        import sympy
    """)


@importorskip('bokeh')
def test_bokeh(pyi_builder):
    pyi_builder.test_source("""
        import bokeh
    """)


@importorskip('xyzservices')
def test_xyzservices(pyi_builder):
    pyi_builder.test_source("""
        import xyzservices.providers
        print(xyzservices.providers.CartoDB)
    """)


@importorskip('mistune')
def test_mistune(pyi_builder):
    pyi_builder.test_source("""
        import mistune
    """)


@importorskip('jsonschema')
def test_jsonschema(pyi_builder):
    pyi_builder.test_source("""
        import jsonschema

        # Sample schema
        schema = {
            "type" : "object",
            "properties" : {
                "price" : {"type" : "number"},
                "name" : {"type" : "string"},
            },
        }

        jsonschema.validate(instance={"name" : "Eggs", "price" : 3.38}, schema=schema)

        try:
            jsonschema.validate(instance={"name" : "Eggs", "price" : "Invalid"}, schema=schema)
        except jsonschema.ValidationError as e:
            print(f"Validation error: {e}")
    """)


@importorskip('psutil')
def test_psutil(pyi_builder):
    pyi_builder.test_source("""
        import psutil
    """)


@importorskip('litestar')
def test_litestar(pyi_builder):
    pyi_builder.test_source("""
        from litestar import Litestar, get
        from litestar.testing import TestClient
        from typing import Dict, Any


        @get("/sync", sync_to_thread=False)
        def sync_hello_world() -> Dict[str, Any]:
            return {"hello": "world"}


        app = Litestar(route_handlers=[sync_hello_world])
        client = TestClient(app)
        response = client.get("/sync")
        assert response.status_code == 200
        assert response.json() == {"hello": "world"}
    """)


@importorskip('lingua')
def test_lingua_language_detector(pyi_builder):
    pyi_builder.test_source("""
        from lingua import Language, LanguageDetectorBuilder

        languages = [Language.ENGLISH, Language.FRENCH, Language.GERMAN, Language.SPANISH]
        detector = LanguageDetectorBuilder.from_languages(*languages).build()

        assert detector.detect_language_of("languages are awesome") == Language.ENGLISH
    """)


@importorskip('opencc')
def test_opencc(pyi_builder):
    pyi_builder.test_source("""
        import opencc

        cc = opencc.OpenCC('s2t')

        assert cc.convert('开放中文转换') == '開放中文轉換'
    """)


@importorskip('jieba')
def test_jieba(pyi_builder):
    pyi_builder.test_source("""
        import jieba

        assert jieba.lcut('我来到北京清华大学') == ['我', '来到', '北京', '清华大学']
    """)


@importorskip('simplemma')
def test_simplemma(pyi_builder):
    pyi_builder.test_source("""
        import simplemma

        assert simplemma.lemmatize('tests', lang='en') == 'test'
    """)


@importorskip('wordcloud')
def test_wordcloud(pyi_builder):
    pyi_builder.test_source("""
        import wordcloud

        wordcloud.WordCloud().generate('test')
    """)


@importorskip('eng_to_ipa')
def test_eng_to_ipa(pyi_builder):
    pyi_builder.test_source("""
        import eng_to_ipa
    """)


@importorskip('mecab')
def test_mecab(pyi_builder):
    pyi_builder.test_source("""
        import mecab

        mecab.MeCab()
    """)


@importorskip('khmernltk')
def test_khmernltk(pyi_builder):
    pyi_builder.test_source("""
        import khmernltk
    """)


@importorskip('pycrfsuite')
def test_pycrfsuite(pyi_builder):
    pyi_builder.test_source("""
        import pycrfsuite
    """)


@importorskip('pymorphy3')
def test_pymorphy3(pyi_builder):
    # Language availability depends on installed packages.
    available_languages = []
    if can_import_module('pymorphy3_dicts_ru'):
        available_languages.append('ru')
    if can_import_module('pymorphy3_dicts_uk'):
        available_languages.append('uk')

    pyi_builder.test_source("""
        import sys
        import pymorphy3

        languages = sys.argv[1:]
        print(f"Languages to test: {languages}")

        for language in languages:
            pymorphy3.MorphAnalyzer(lang=language)
    """, app_args=available_languages)


@importorskip('sudachipy')
@importorskip('sudachidict_small')
@importorskip('sudachidict_core')
@importorskip('sudachidict_full')
def test_sudachipy(pyi_builder):
    pyi_builder.test_source("""
        from sudachipy import Dictionary

        Dictionary(dict='small').create()
        Dictionary(dict='core').create()
        Dictionary(dict='full').create()
    """)


@importorskip('laonlp')
def test_laonlp(pyi_builder):
    pyi_builder.test_source("""
        import laonlp
    """)


@importorskip('pythainlp')
def test_pythainlp(pyi_builder):
    pyi_builder.test_source("""
        import pythainlp
    """)


@importorskip('gmsh')
def test_gmsh(pyi_builder):
    pyi_builder.test_source("""
        import gmsh
    """)


@importorskip('sspilib')
def test_sspilib(pyi_builder):
    pyi_builder.test_source("""
        import sspilib

        cred = sspilib.UserCredential(
            "username@DOMAIN.COM",
            "password",
        )

        ctx = sspilib.ClientSecurityContext(
            "host/server.domain.com",
            credential=cred,
        )

        print(ctx)
    """)


@importorskip('rlp')
def test_rlp(pyi_builder):
    pyi_builder.test_source("""
        import rlp
    """)


@importorskip('eth_rlp')
def test_eth_rlp(pyi_builder):
    pyi_builder.test_source("""
        import eth_rlp
    """)


@importorskip('z3c.rml')
def test_z3c_rml_rml2pdf(pyi_builder):
    pyi_builder.test_source("""
        from z3c.rml import rml2pdf

        rml = '''
        <!DOCTYPE document SYSTEM "rml.dtd" >
        <document filename="test.pdf">
          <template showBoundary="1">
            <!--Debugging is now turned on, frame outlines -->
            <!--will appear on the page -->
            <pageTemplate id="main">
              <!-- two frames are defined here: -->
              <frame id="first" x1="100" y1="400" width="150" height="200" />
              <frame id="second" x1="300" y1="400" width="150" height="200" />
            </pageTemplate>
          </template>
          <stylesheet><!-- still empty...--></stylesheet>
          <story>
            <para>Welcome to RML.</para>
          </story>
        </document>
        '''

        pdf_bytes = rml2pdf.parseString(rml)
    """)


@importorskip('freetype')
def test_pyi_freetype(pyi_builder):
    pyi_builder.test_source("""
        import sys
        import pathlib

        import freetype

        # Ensure that the freetype shared library is bundled with the frozen application; otherwise, freetype might be
        # using system-wide library.

        # First, check that freetype.FT_Library_filename is an absolute path; otherwise, it is likely using
        # basename-only ctypes fallback.
        ft_library_file = pathlib.Path(freetype.FT_Library_filename)
        print(f"FT library file (original): {ft_library_file}", file=sys.stderr)
        assert ft_library_file.is_absolute(), "FT library file is not an absolute path!"

        # Check that fully-resolved freetype.FT_Library_filename is anchored in fully-resolved frozen application
        # directory.
        app_dir = pathlib.Path(__file__).resolve().parent
        print(f"Application directory: {app_dir}", file=sys.stderr)
        ft_library_path = pathlib.Path(ft_library_file).resolve()
        print(f"FT library file (resolved): {ft_library_path}", file=sys.stderr)
        assert app_dir in ft_library_path.parents, "FT library is not bundled with frozen application!"
    """)


@importorskip('vaderSentiment')
def test_vadersentiment(pyi_builder):
    pyi_builder.test_source("""
        import vaderSentiment.vaderSentiment
        vaderSentiment.vaderSentiment.SentimentIntensityAnalyzer()
    """)


@importorskip('langchain')
def test_langchain_llm_summarization_checker(pyi_builder):
    pyi_builder.test_source("""
        import langchain.chains.llm_summarization_checker.base
    """)


@importorskip('seedir')
def test_seedir(pyi_builder):
    pyi_builder.test_source("""
        import seedir
    """)
