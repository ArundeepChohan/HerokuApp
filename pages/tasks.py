from celery import task


@task()
def echoe():
    """
    A simple task that echoes a Hello World! text to celery console.
    """
    print('Hello World!')