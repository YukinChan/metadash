import logging
from .celery import celery


def _is_celery_avaliable():
    # XXX: Change to is_async_avaliable after we have single redis url config
    if celery is not None:
        return True
    logger.info("Celery backend not found.")
    return False


logger = logging.getLogger(__name__)


def get_active_workers():
    if not _is_celery_avaliable():
        return {}
    # Get all running (active) jobs grouped by worker
    workers = celery.control.inspect().active()
    if workers is None:
        logger.info("Celery worker not found")
        return {}
    return workers


def get_running_task_status():
    if not _is_celery_avaliable():
        return []
    task_status = []
    workers = get_active_workers()
    for worker, tasks in workers.items():
        for task in tasks:
            res = celery.AsyncResult(task['id'])
            task_status.append({
                'name': task['name'],
                'id': task['id'],
                'state': res.state,
                'meta': res.info
            })
    return task_status


def cancel_task(task_ids=[]):
    if not _is_celery_avaliable():
        return {}
    task_status = {}
    worker_tasks = get_active_workers()
    for worker, tasks in worker_tasks.items():
        for task in tasks:
            res = celery.AsyncResult(task['id'])
            task_status[task['name']] = {
                'state': res.state,
                'meta': res.info
            }
            if task['id'] in task_ids:
                res.revoke(terminate=True)
                task_status[task['name']]['canceled'] = True
    return task_status
