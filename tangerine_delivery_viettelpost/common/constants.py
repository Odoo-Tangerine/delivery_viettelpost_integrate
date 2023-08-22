from enum import Enum
from typing import List, Tuple, Sequence, Final


class Constants(Enum):
    VIETTELPOST_URL: Final[str] = 'https://partner.viettelpost.vn'
    VIETTELPOST_PRODUCT_TYPES: Final[List[Sequence[Tuple]]] = [('TH', 'Envelope'), ('HH', 'Goods')]
    VIETTELPOST_NATIONAL_TYPES: Final[List[Sequence[Tuple]]] = [('1', 'Inland'), ('0', 'International')]
    VIETTELPOST_ORDER_PAYMENT: Final[List[Sequence[Tuple]]] = [
        ('1', 'Uncollect money'),
        ('2', 'Collect express fee and price of goods'),
        ('3', 'Collect price of goods'),
        ('4', 'Collect express fee')
    ]
    VIETTELPOST_PRINT_URL_A5: Final[str] = 'https://digitalize.viettelpost.vn/DigitalizePrint/report.do?type=1&bill={}&showPostage=1'
    VIETTELPOST_PRINT_URL_A6: Final[str] = 'https://digitalize.viettelpost.vn/DigitalizePrint/report.do?type=2&bill={}&showPostage=1'
    VIETTELPOST_PRINT_URL_A7: Final[str] = 'https://digitalize.viettelpost.vn/DigitalizePrint/report.do?type=1001&bill={}&showPostage=1'


