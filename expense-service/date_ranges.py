import calendar
from fastapi import HTTPException, status
from datetime import date

def get_month_ranges(month_name : str):
    cleaned_month = month_name.strip().capitalize()
    try:
        month_list = list(calendar.month_name)
        month_number = month_list.index(cleaned_month)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Month name")
    current_year = date.today().year
    start_date = date(current_year,month_number,1)
    _, total_days = calendar.monthrange(current_year,month_number)
    end_date = date(current_year,month_number,total_days)
    return start_date,end_date 