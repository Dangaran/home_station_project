from requests_html import HTMLSession
import datetime


def get_aemet_data(url):
    output = {}
    try:
        # extract html from url
        session = HTMLSession()
        response = session.get(url)
        
        # get hour
        now = datetime.datetime.now()
        hour_to_compare = now.hour

        # get only first row from the table
        row_to_save = response.html.xpath('//*[@class="fila_hora cabecera_niv2"]')[0]

        # check hour and select next row if necessary
        hour_from_aemet = row_to_save.xpath('.//td')[0].xpath('.//td/text()')[0].strip()
        if hour_from_aemet != hour_to_compare:
            row_to_save = response.html.xpath('//*[@class="fila_hora cabecera_niv2"]')[1]

        print(row_to_save.xpath('.//td')[9].xpath('.//td/text()')[0].strip().split('%'))
        print(row_to_save.xpath('.//td')[10].xpath('.//td/text()')[0].strip().strip().split('%')[0])
        print(row_to_save.xpath('.//td')[11].xpath('.//td/text()')[0].strip().strip().split('%')[0])
        print(row_to_save.xpath('.//td')[12].xpath('.//td/@class')[0].strip().split(' ')[1])
        
        # extract data from the row
        output = {
            'hour': row_to_save.xpath('.//td')[0].xpath('.//td/text()')[0].strip(),
            'sky': row_to_save.xpath('.//td')[1].xpath('.//td/img/@title')[0].strip(),
            'temperature': row_to_save.xpath('.//td')[2].xpath('.//td/text()')[0].strip(),
            'thermal_sensation': row_to_save.xpath('.//td')[3].xpath('.//td/text()')[0].strip(),
            'wind_direction': row_to_save.xpath('.//td')[4].xpath('.//*[@class="texto_viento"]/text()')[0].strip(),
            'avg_wind_speed': row_to_save.xpath('.//td')[4].xpath('.//*[@class="texto_km_viento"]/div/text()')[0].strip(),
            'max_wind_speed': row_to_save.xpath('.//td')[5].xpath('.//td/text()')[0].strip(),
            'precipitation': row_to_save.xpath('.//td')[6].xpath('.//td/text()')[0].strip(),
            'snow': row_to_save.xpath('.//td')[7].xpath('.//td/text()')[0].strip(),
            'relative_humidity': row_to_save.xpath('.//td')[8].xpath('.//td/text()')[0].strip(),
            'precipitation_probability': row_to_save.xpath('.//td')[9].xpath('.//td/text()')[0].strip().split('%')[0],
            'snow_probability': row_to_save.xpath('.//td')[10].xpath('.//td/text()')[0].strip().strip().split('%')[0],
            'storm_probability': row_to_save.xpath('.//td')[11].xpath('.//td/text()')[0].strip().strip().split('%')[0],
            'warning_level': row_to_save.xpath('.//td')[12].xpath('.//td/@class')[0].strip().split(' ')[1]
        }

    except Exception as e:
        print(e)
        print('Something went wrong, check function "get_aemet_data"')

    return output

