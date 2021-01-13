from celery import shared_task


@shared_task(queue='fetch_fills', bind=True)
def fetch_fills(self):
    print('Cellery fetch fills works')

    return True


@shared_task(queue='generate_trades', bind=True)
def generate_trades(self):

    return 'Cellery generate task works'
