import sys
from qutils.utils import *

if __name__ == '__main__':
    print(get_n_days('20210801', 7))
    print(get_date())
    code = 'US.AAPL210910C152500'
    print(parse_strike_timestamp(code))
