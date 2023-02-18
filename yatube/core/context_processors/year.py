from datetime import datetime
time_now = datetime.now()
time_now = time_now.year


def year(request):
    """Добавляет переменную с текущим годом."""
    return {
        'year': time_now
    }
