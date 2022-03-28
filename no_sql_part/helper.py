import datetime


def date_range_obtainer(days):
    result = []
    resultStr = ""
    # Months | Get Year
    if days == 365:
        for x in range(0, days):
            # Returns Month Format
            rangeDate = datetime.datetime.now() - datetime.timedelta(days=x)
            newRange = rangeDate.strftime("%Y-%m")
            resultStr = newRange
            if (len(result) == 0):
                result.append(resultStr)
            elif (len(result) != 0):
                if (result[-1] != resultStr):
                    result.append(resultStr)

    # Get 24H, 7D, 1M
    elif days == 1 or days == 7 or days == 30:
        # Days
        for x in range(0, days):
            # Returns Dates Format
            rangeDate = datetime.datetime.now() - datetime.timedelta(days=x)
            newRange = rangeDate.strftime("%Y-%m-%d")
            resultStr = newRange
            result.append(resultStr)
    # Get All
    else:
        obtainDays = datetime.datetime.now() - datetime.datetime(2020, 1, 1)
        days = obtainDays.days
        for x in range(0, days):
            # Returns Month Format
            rangeDate = datetime.datetime.now() - datetime.timedelta(days=x)
            newRange = rangeDate.strftime("%Y-%m")
            resultStr = newRange
            if (len(result) == 0):
                result.append(resultStr)
            elif (len(result) != 0):
                if (result[-1] != resultStr):
                    result.append(resultStr)

    return result
