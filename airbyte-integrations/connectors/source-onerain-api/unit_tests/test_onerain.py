"""
unit tests for ONeRain source connector
"""

# format anchor
import pytest
from source_onerain_api import source
import xmltodict
from collections import OrderedDict

onerain_response_multi_row="""
<onerain>
   <response>
      <general>
         <row>
            <or_site_id>817</or_site_id>
            <site_id>54-0000-Leasburg_River_Cable</site_id>
            <location>River Gauge 3 - Leasburg Cable</location>
            <owner>DEPRECATED</owner>
            <system_id>6</system_id>
            <client_id>766b01af-4e22-445b-9ba1-145c3086d7b2</client_id>
            <latitude_dec>32.4769140</latitude_dec>
            <longitude_dec>-106.9197700</longitude_dec>
            <elevation>0</elevation>
         </row>
         <row>
            <or_site_id>817</or_site_id>
            <site_id>54-0000-Leasburg_River_Cable</site_id>
            <location>River Gauge 3 - Leasburg Cable</location>
            <owner>DEPRECATED</owner>
            <system_id>6</system_id>
            <client_id>766b01af-4e22-445b-9ba1-145c3086d7b2</client_id>
            <latitude_dec>32.4769140</latitude_dec>
            <longitude_dec>-106.9197700</longitude_dec>
            <elevation>0</elevation>
         </row>
      </general>
   </response>
</onerain>"""

onerain_response_single_row="""
<onerain>
   <response>
      <general>
         <row>
            <or_site_id>817</or_site_id>
            <site_id>54-0000-Leasburg_River_Cable</site_id>
            <location>River Gauge 3 - Leasburg Cable</location>
            <owner>DEPRECATED</owner>
            <system_id>6</system_id>
            <client_id>766b01af-4e22-445b-9ba1-145c3086d7b2</client_id>
            <latitude_dec>32.4769140</latitude_dec>
            <longitude_dec>-106.9197700</longitude_dec>
            <elevation>0</elevation>
         </row>
      </general>
   </response>
</onerain>
"""
onerain_response_no_row="""
<onerain>
   <response>
      <general/>
   </response>
</onerain>
"""

def test_add_time_days():

    dt = "1989-01-03 21:12:09"
    assert source.add_time_days(dt,1)  == "1989-01-04 21:12:09"

    dt = "2005-03-31 09:03:12"
    assert source.add_time_days(dt,3) == "2005-04-03 09:03:12"

    with pytest.raises(ValueError):
        source.add_time_days("03/04/1923",1)

    with pytest.raises(TypeError):
        source.add_time_days(dt,"1")

    # test leap year
    dt = "2020-02-28 00:00:00"
    assert source.add_time_days(dt,1) == "2020-02-29 00:00:00"

    dt_fmt = "2020-01-%02d 12:12:12"
    for x in range(30):
        dt = dt_fmt % (x+1)
        dt2 = source.add_time_days(dt,1)
        assert dt2 == dt_fmt % (x+2)

def test_diff_days():

    d1="2005-03-12 05:30:23"
    d2="2005-03-13 05:29:23"
    assert source.diff_days(d2,d1) == 0

    d2="2005-03-13 05:30:23"
    assert source.diff_days(d2,d1) == 1

    d1="2020-06-01 05:11:18"
    d2="2020-06-15 05:11:17"
    assert source.diff_days(d2,d1) == 13
    
    assert source.diff_days(d1,d2) < 0

def test_data_range():

    dt_start="1971-12-01 12:13:04"
    dt_end="1971-12-20 00:00:00"
  
     
    day=1 
    inc_days=1
    loop_count=0
    for start,end in source.data_range(dt_start,dt_end,inc_days):
        loop_count=loop_count+1
        expected_start = "1971-12-%02d 12:13:04" % day
        expected_end = "1971-12-%02d 12:13:04" % (day+inc_days)
        if loop_count < 19:
            assert expected_start == start
            assert expected_end == end
        else:
            assert expected_start == start
            assert end == dt_end
        day=day+1

    assert loop_count==19

def test_onerain_response():
    response_single_row = xmltodict.parse(onerain_response_single_row)
    row=response_single_row['onerain']['response']['general']['row']
    assert isinstance(row,OrderedDict)
    assert 'row' in response_single_row['onerain']['response']['general']

    response_multi_row = xmltodict.parse(onerain_response_multi_row)
    row=response_multi_row['onerain']['response']['general']['row']
    assert isinstance(row,list)


    response_no_row = xmltodict.parse(onerain_response_no_row)
    general = response_no_row['onerain']['response']['general']
    assert isinstance(general,type(None))

    with pytest.raises(KeyError):
        response_multi_row['onerain']['response']['general']['rows']

