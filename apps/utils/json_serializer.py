from datetime import datetime, date


def json_serializer(obj):

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    else:
        return obj.__dict__
