# -*- coding: utf-8 -*-
"""
Created on Fri Oct 29 14:25:36 2021
@author: Buitink
"""

import os
import click
import hydromt
import cdsapi
import xarray as xr
from dateutil.relativedelta import relativedelta
from datetime import datetime

@click.command()
@click.option('--output_dir', required=True, type=str,
              help='Output directory for downloaded files (orography and forcing files)',)
@click.option('--date_string', required=True, type=str,
              help='String with year and month of current month (in YYYY_MM format)',)
@click.option('--staticmaps_fn', required=True, type=str,
              help='Path to the staticmaps file, used to determine model extent',)

# Optional settings
@click.option('--buffer', default=0.5,
              type=float, help='Buffer around model domain to ensure region for ERA5 and SEAS5 downloads, in degrees')
def download_forcing(output_dir, date_string, staticmaps_fn, buffer):

    # Get current date, for month and year information
    current_date = datetime.strptime(date_string, '%Y_%m').date()
    current_month = current_date.month
    current_year = current_date.year

    previous_date = current_date - relativedelta(months=1)
    prev_month = previous_date.month
    prev_year = previous_date.year


    # Extract area from model input
    area_str, area_list = get_area_from_staticmaps(staticmaps_fn=staticmaps_fn, buffer=buffer)

    # Download orography files (sliced to the required area)
    download_era5_orography(output=output_dir, area=area_list)
    download_seas5_orography(output=output_dir, area=area_list)

    # Download ERA5 data
    download_era5(month=prev_month, year=prev_year, output=output_dir, area=area_str)
    # Download SEAS5 data
    download_seas5(month=current_month, year=current_year, output=output_dir, area=area_str)


def get_area_from_staticmaps(staticmaps_fn, buffer):

    # Read staticmaps file
    staticmaps = xr.open_dataset(staticmaps_fn)

    # Get the bounding box of the staticmaps
    bbox = staticmaps.raster.box.bounds.loc[0]
    # Determine the bounding box, and apply a buffer to ensure that the downloaded
    # data is big enough for the model domain
    xmin = bbox["minx"] - buffer
    xmax = bbox["maxx"] + buffer
    ymin = bbox["miny"] - buffer
    ymax = bbox["maxy"] + buffer

    # Round to nearest 0.5 value
    xmin = float(round((xmin*2))/2)
    xmax = float(round((xmax*2))/2)
    ymin = float(round((ymin*2))/2)
    ymax = float(round((ymax*2))/2)

    # Set the bounding box to the correct format, such that it can be used by
    # the ERA5 and SEAS5 download scripts
    area_str = f"{ymin:.2f}/{xmin:.2f}/{ymax:.2f}/{xmax:.2f}"
    area_list = [ymin, xmin, ymax, xmax]

    return area_str, area_list


def download_era5_orography(output, area):
    """Download ERA5 orography file """

    output_path = os.path.join(output, "orography_era5.grib")

    c = cdsapi.Client()

    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            'product_type': 'reanalysis',
            'variable': 'geopotential',
            'area': area,
            'year': '2018',
            'month': '01',
            'day': '01',
            'time': '00:00',
            'format': 'grib',
        },
        output_path)

def download_seas5_orography(output, area):

    output_path = os.path.join(output, "orography_seas5.grib")

    c = cdsapi.Client()

    c.retrieve(
        'seasonal-original-single-levels',
        {
            'originating_centre': 'ecmwf',
            'system': '5',
            'variable': 'orography',
            'area': area,
            'year': '2016',
            'month': '01',
            'day': '01',
            'leadtime_hour': '0',
            'format': 'grib',
        },
        output_path)

def download_era5(month, year, output, area):
    """Download ERA5 data."""
    c = cdsapi.Client()

    filename = f'ERA5_{year}_{month}.nc'
    output_path = os.path.join(output, filename)

    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            'product_type':'reanalysis',
            'variable': [
                'mean_sea_level_pressure',
                'surface_solar_radiation_downwards',
                '2m_temperature',
                'total_precipitation'
            ],
            'year':year,
            'area': area,
            'month':month,
            'day':[
                '01','02','03',
                '04','05','06',
                '07','08','09',
                '10','11','12',
                '13','14','15',
                '16','17','18',
                '19','20','21',
                '22','23','24',
                '25','26','27',
                '28','29','30',
                '31'
            ],
            'time':[
                '00:00','01:00','02:00',
                '03:00','04:00','05:00',
                '06:00','07:00','08:00',
                '09:00','10:00','11:00',
                '12:00','13:00','14:00',
                '15:00','16:00','17:00',
                '18:00','19:00','20:00',
                '21:00','22:00','23:00'
            ],
            'format':'netcdf'
        },

        output_path)

def download_seas5(month, year, output, area):
    """Download SEAS5 data."""
    c = cdsapi.Client()

    filename = f'SEAS5_{year}_{month}.nc'
    output_path = os.path.join(output, filename)

    c.retrieve(
        'seasonal-original-single-levels',
        {
            'originating_centre':'ecmwf',
            'system':'5',
            'variable': [
                'mean_sea_level_pressure',
                'surface_solar_radiation_downwards',
                '2m_temperature',
                'total_precipitation'
            ],
            'year':[
                year
            ],
            'area': area,
            'month':[month],
            'day':['01'],
            'leadtime_hour':[
                '6','12','18', '24','30','36',
                '42','48','54', '60','66','72',
                '78','84','90', '96','102','108',
                '114','120','126', '132','138','144',
                '150','156','162', '168','174','180',
                '186','192','198', '204','210','216',
                '222','228','234', '240','246','252',
                '258','264','270', '276','282','288',
                '294','300','306', '312','318','324',
                '330','336','342', '348','354','360',
                '366','372','378', '384','390','396',
                '402','408','414', '420','426','432',
                '438','444','450', '456','462','468',
                '474','480','486', '492','498','504',
                '510','516','522', '528','534','540',
                '546','552','558', '564','570','576',
                '582','588','594', '600','606','612',
                '618','624','630', '636','642','648',
                '654','660','666', '672','678','684',
                '690','696','702', '708','714','720',
                '726','732','738', '744','750','756',
                '762','768','774', '780','786','792',
                '798','804','810', '816','822','828',
                '834','840','846', '852','858','864',
                '870','876','882', '888','894','900',
                '906','912','918', '924','930','936',
                '942','948','954', '960','966','972',
                '978','984','990', '996','1002','1008',
                '1014','1020','1026', '1032','1038','1044',
                '1050','1056','1062', '1068','1074','1080',
                '1086','1092','1098', '1104','1110','1116',
                '1122','1128','1134', '1140','1146','1152',
                '1158','1164','1170', '1176','1182','1188',
                '1194','1200','1206', '1212','1218','1224',
                '1230','1236','1242', '1248','1254','1260',
                '1266','1272','1278', '1284','1290','1296',
                '1302','1308','1314', '1320','1326','1332',
                '1338','1344','1350', '1356','1362','1368',
                '1374','1380','1386', '1392','1398','1404',
                '1410','1416','1422', '1428','1434','1440',
                '1446','1452','1458', '1464','1470','1476',
                '1482','1488','1494', '1500','1506','1512',
                '1518','1524','1530', '1536','1542','1548',
                '1554','1560','1566', '1572','1578','1584',
                '1590','1596','1602', '1608','1614','1620',
                '1626','1632','1638', '1644','1650','1656',
                '1662','1668','1674', '1680','1686','1692',
                '1698','1704','1710', '1716','1722','1728',
                '1734','1740','1746', '1752','1758','1764',
                '1770','1776','1782', '1788','1794','1800',
                '1806','1812','1818', '1824','1830','1836',
                '1842','1848','1854', '1860','1866','1872',
                '1878','1884','1890', '1896','1902','1908',
                '1914','1920','1926', '1932','1938','1944',
                '1950','1956','1962', '1968','1974','1980',
                '1986','1992','1998', '2004','2010','2016',
                '2022','2028','2034', '2040','2046','2052',
                '2058','2064','2070', '2076','2082','2088',
                '2094','2100','2106', '2112','2118','2124',
                '2130','2136','2142', '2148','2154','2160',
                '2166','2172','2178', '2184','2190','2196',
                '2202','2208','2214', '2220','2226','2232',
                '2238','2244','2250', '2256','2262','2268',
                '2274','2280','2286', '2292','2298','2304',
                '2310','2316','2322', '2328','2334','2340',
                '2346','2352','2358', '2364','2370','2376',
                '2382','2388','2394', '2400','2406','2412',
                '2418','2424','2430', '2436','2442','2448',
                '2454','2460','2466', '2472','2478','2484',
                '2490','2496','2502', '2508','2514','2520',
                '2526','2532','2538', '2544','2550','2556',
                '2562','2568','2574', '2580','2586','2592',
                '2598','2604','2610', '2616','2622','2628',
                '2634','2640','2646', '2652','2658','2664',
                '2670','2676','2682', '2688','2694','2700',
                '2706','2712','2718', '2724','2730','2736',
                '2742','2748','2754', '2760','2766','2772',
                '2778','2784','2790', '2796','2802','2808',
                '2814','2820','2826', '2832','2838','2844',
                '2850','2856','2862', '2868','2874','2880',
                '2886','2892','2898', '2904','2910','2916',
                '2922','2928','2934', '2940','2946','2952',
                '2958','2964','2970', '2976','2982','2988',
                '2994','3000','3006', '3012','3018','3024',
                '3030','3036','3042', '3048','3054','3060',
                '3066','3072','3078', '3084','3090','3096',
                '3102','3108','3114', '3120','3126','3132',
                '3138','3144','3150', '3156','3162','3168',
                '3174','3180','3186', '3192','3198','3204',
                '3210','3216','3222', '3228','3234','3240',
                '3246','3252','3258', '3264','3270','3276',
                '3282','3288','3294', '3300','3306','3312',
                '3318','3324','3330', '3336','3342','3348',
                '3354','3360','3366', '3372','3378','3384',
                '3390','3396','3402', '3408','3414','3420',
                '3426','3432','3438', '3444','3450','3456',
                '3462','3468','3474', '3480','3486','3492',
                '3498','3504','3510', '3516','3522','3528',
                '3534','3540','3546', '3552','3558','3564',
                '3570','3576','3582', '3588','3594','3600',
                '3606','3612','3618', '3624','3630','3636',
                '3642','3648','3654', '3660','3666','3672',
                '3678','3684','3690', '3696','3702','3708',
                '3714','3720','3726', '3732','3738','3744',
                '3750','3756','3762', '3768','3774','3780',
                '3786','3792','3798', '3804','3810','3816',
                '3822','3828','3834', '3840','3846','3852',
                '3858','3864','3870', '3876','3882','3888',
                '3894','3900','3906', '3912','3918','3924',
                '3930','3936','3942', '3948','3954','3960',
                '3966','3972','3978', '3984','3990','3996',
                '4002','4008','4014', '4020','4026','4032',
                '4038','4044','4050', '4056','4062','4068',
                '4074','4080','4086', '4092','4098','4104',
                '4110','4116','4122', '4128','4134','4140',
                '4146','4152','4158', '4164','4170','4176',
                '4182','4188','4194', '4200','4206','4212',
                '4218','4224','4230', '4236','4242','4248',
                '4254','4260','4266', '4272','4278','4284',
                '4290','4296','4302', '4308','4314','4320',
                '4326','4332','4338', '4344','4350','4356',
                '4362','4368','4374', '4380','4386','4392',
                '4398','4404','4410', '4416','4422','4428',
                '4434','4440','4446', '4452','4458','4464',
                '4470','4476','4482', '4488','4494','4500',
                '4506','4512','4518', '4524','4530','4536',
                '4542','4548','4554', '4560','4566','4572',
                '4578','4584','4590', '4596','4602','4608',
                '4614','4620','4626', '4632','4638','4644',
                '4650','4656','4662', '4668','4674','4680',
                '4686','4692','4698', '4704','4710','4716',
                '4722','4728','4734', '4740','4746','4752',
                '4758','4764','4770', '4776','4782','4788',
                '4794','4800','4806', '4812','4818','4824',
                '4830','4836','4842', '4848','4854','4860',
                '4866','4872','4878', '4884','4890','4896',
                '4902','4908','4914', '4920','4926','4932',
                '4938','4944','4950', '4956','4962','4968',
                '4974','4980','4986', '4992','4998','5004',
                '5010','5016','5022', '5028','5034','5040',
                '5046','5052','5058', '5064','5070','5076',
                '5082','5088','5094', '5100','5106','5112',
                '5118','5124','5130', '5136','5142','5148',
                '5154','5160'
                    ],
            'format':'netcdf'
        },

        output_path)


if __name__ == '__main__':
    download_forcing()

    # LOCAL TESTING
    # output_dir = r"c:\Users\buitink\Documents\Projects\cscale\testing\downloads\\"
    # date_string = "2022_04"
    # staticmaps_fn = r"c:\Users\buitink\Documents\Projects\cscale\wflow_rhine\staticmaps.nc"
    # buffer = 0.5
    # download_forcing(output_dir=output_dir,
    #                  date_string=date_string,
    #                  staticmaps_fn=staticmaps_fn,
    #                  buffer=0.5)

    # Old area rhine: '46.00/5.00/52.50/12.50'
    # download_era5(month=2, year=2022, output="workdir")
    # download_seas5(month=2, year=2022, output="workdir")

    # area = '46.00/5.00/52.50/12.50'
    # download_era5_orography(output="test", area=area)
    # download_seas5_orography(output="test", area=area)