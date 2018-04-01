from very.core.tasks import task


@task('add')
def add(x, y):
    return x + y


@task('sub')
def sub(x, y):
    return x - y


@task('mul')
def mul(x, y):
    return x * y


@task('div')
def div(x, y):
    return x / y
