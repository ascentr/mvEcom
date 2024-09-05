from datetime import date , time , datetime 

#[('12:00 AM' , '12:00 AM') , ('12:30 AM' , '12:30 AM') , ('12:00 PM' , '12:00 PM') ]

# for h in range (0,24):
#     for m in (0, 30):
#         print(time(h, m).strftime('%I:%M %p'))

t = [ ( time(h , m).strftime('%I:%M %p'),  time(h , m).strftime('%I:%M %p')) for h in range(0,24) for m in (0,30) ]
#print(t)

date_today = date.today()
now = datetime.now()  #2023-07-18 12:27:01.035395
now_year = now.strftime("%Y") , now.strftime("%m") , now.strftime("%d")
#print(now_year)

current_time= now.strftime("%H:%M:%S %p")
#print(date_today , type(date_today))
# print(now)
#print(current_time)



a = time(00,12,15)  #00:12:15
c = time(hour = 11, minute = 34, second = 56)

from_time = '12:30 AM'
to_time = '02:30 AM'

start = str(datetime.strptime( from_time, "%I:%M %p").time())
end = str(datetime.strptime(to_time, '%I:%M %p').time())
print( "current time ::>" ,  current_time)
print(start , ' ||' , end )
if current_time > start and current_time < end:
    print("OPEN")
else:
    print("CLOSED")




