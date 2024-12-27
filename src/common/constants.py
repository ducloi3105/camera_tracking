import os
import re

import config

TMP_DIR = os.path.join(config.ROOT_PATH, 'tmp')
if not os.path.exists(TMP_DIR):
    try:
        os.makedirs(TMP_DIR)
    except FileExistsError as e:
        print('TMP existed', e)

VALID_IMAGE_FORMATS = ['jpeg', 'jpg', 'png', 'webp']

ISO_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

ISO8601_DATETIME_RE = re.compile(
    r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})'
    r'[T ](?P<hour>\d{1,2}):(?P<minute>\d{1,2})'
    r'(?::(?P<second>\d{1,2})(?:\.(?P<microsecond>\d{1,6})\d{0,6})?)?'
    r'(?P<tzinfo>Z|[+-]\d{2}(?::?\d{2})?)?$'
)

DATE_FORMATS = [
    dict(
        id='dd/mm/yyyy',
        js_moment='DD/MM/YYYY',
        js_element='dd/MM/yyyy',
        py='%d/%m/%Y',
        example='30/12/2020'
    ),
    dict(
        id='yyyy/mm/dd',
        js_moment='YYYY/MM/DD',
        js_element='yyyy/MM/dd',
        py='%Y/%m/%d',
        example='2020/12/30'
    ),
    dict(
        id='mm/dd/yyyy',
        js_moment='MM/DD/YYYY',
        js_element='MM/dd/yyyy',
        py='%m/%d/%Y',
        example='01/20/2020'
    )
]

TIME_FORMATS = [
    dict(
        id='hh:mm',
        js_moment='HH:mm',
        js_element='HH:mm',
        py='%H:%M',
        example='16:50'
    ),
    dict(
        id='hh:mm A',
        js_moment='hh:mm A',
        js_element='hh:mm A',
        py='%I:%M %p',
        example='07:50 PM'
    )
]

STRING_LENGTH = {
    'UUID4': 36,
    'EX_SHORT': 50,
    'SHORT': 100,
    'MEDIUM': 500,
    'LONG': 2000,
    'EX_LONG': 10000,
    'LARGE': 30000,
    'EX_LARGE': 200000
}

PAGINATION = {
    'page': 1,
    'per_page': 20
}

PHONE_REGEX = r'^(\+8[0-9]{9,12})$|^(0[0-9]{6,15})$'

DEFAULT_USER_STATUS = 'active'
DEFAULT_LANGUAGE = 'en-US'

HTTP_METHODS = [
    'GET',
    'PUT',
    'PATCH',
    'POST',
    'DELETE'
]


LANGUAGES = [
    ('fr-FR', 'French'),
    ('ar-SA', 'Arabic'),
    ('vi-VN', 'Vietnamese'),
    ('cs-CZ', 'Czech'),
    ('da-DK', 'Danish'),
    ('nl-NL', 'Dutch'),
    ('fi-FI', 'Finnish'),
    ('fr-CA', 'French (Canada)'),
    ('de-DE', 'German'),
    ('el-GR', 'Greek'),
    ('hu-HU', 'Hungarian'),
    ('is-IS', 'Icelandic'),
    ('id-ID', 'Indonesian'),
    ('it-IT', 'Italian'),
    ('ja-JP', 'Japanese'),
    ('ko-KR', 'Korean'),
    ('lt-LT', 'Lithuanian'),
    ('ms-MY', 'Malay'),
    ('nb-NO', 'Norwegian'),
    ('pl-PL', 'Polish'),
    ('pt-BR', 'Portuguese (Brazil)'),
    ('pt-PT', 'Portuguese (Portugal)'),
    ('ru-RU', 'Russian'),
    ('sk-SK', 'Slovak'),
    ('es-MX', 'Spanish (Mexico)'),
    ('es-ES', 'Spanish (Spain)'),
    ('sv-SE', 'Swedish'),
    ('th-TH', 'Thai'),
    ('tr-TR', 'Turkish'),
    ('uk-UA', 'Ukrainian'),
    ('en-US', 'English'),
    ('zh-CN', 'Chinese (Simplified)'),
    ('zh-TW', 'Chinese (Traditional)'),
    ('zh-HK', 'Chinese (Hongkong)'),
]


COVID_ATTRIBUTES = [
    "1073745001",
    "1073745002",
    "1073744999",
    "1073745000",
    "1073744995",
    "1073744996",
    "1073744991",
    "1073744992",
    "1073744901",
    "1073744990",
    "1073745003",
    "1073745004",
    "1073744993",
    "1073744994",
    "1073745005",
    "1073745006",
    "1073744997",
    "1073744998",
    "1073744900",
    "1073745012",
    "1073745013",
    "1073745014",
    "1073745009",
    "1073745010",
    "1073745019",
    "1073745020",
    "1073745007",
    "1073745008",
    "1073745017",
    "1073745018",
    "1073745015",
    "1073745016",
    "1073745045",
    "1073745046",
    "1073745011",
    "1073745021",
    "1073745022",
    "1073745060",
    "1073745061",
    "1073745062",
    "1073745063",
    "1073745049",
    "1073745050",
    "1073745056",
    "1073745057",
    "1073745054",
    "1073745055",
    "1073745058",
    "1073745059",
    "1073745051",
    "1073745052",
    "1073745047",
    "1073745048",
    "1073745053",
    "1073745119",
    "1073745120",
    "1073745064",
    "1073745065",
    "1073745066",
    "1073745103",
    "1073745104",
    "1073745105",
    "1073745112",
    "1073745113",
    "1073745115",
    "1073745116",
    "1073745106",
    "1073745107",
    "1073745108",
    "1073745109",
    "1073745114",
    "1073745121",
    "1073745122",
    "1073745123",
    "1073745124",
    "1073745125",
    "1073745126",
    "1073745127"
]

PLACE_TYPES = [
    "airport",
    "city",
    "country",
    "high_level_region",
    "metro_station",
    "multi_city_vicinity",
    "neighborhood",
    "point_of_interest",
    "province_state",
    "train_station"
]

PROPERTY_TYPES = [
    'Others',
    'Hotel',
    'Motel',
    'Resort',
    'Inn',
    'Others',
    'Guesthouse',
    'Condo',
    'Others',
    'Cabin',
    'Chalet',
    'Cottage',
    'Hostel',
    'Ranch',
    'Villa',
    'Lodge',
    'Apartment',
    'Others',
    'Houseboat',
    'Ryokan',
    'Tree house',
    'Aparthotel',
    'Condominium resort',
    'Campsite',
    'Riad',
    'Hostal',
    'Country House',
    'Pension',
    'Pousada Portugal',
    'Pousada Brazil',
    'Residence',
    'TownHouse',
    'Castle',
    'Safari-Tentalow',
    'Palace',
    'Agritourism',
    'Cruise',
    'Holiday Park',
]
