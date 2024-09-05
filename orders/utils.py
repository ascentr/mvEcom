import datetime

# order number format YYYYMMDDHHMM+PK
def generate_order_number(pk):
    current_datetime =  datetime.datetime.now().strftime('%Y%M%d%H%M')
    order_number = current_datetime + str(pk)
    return order_number
