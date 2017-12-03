import atexit
import queue
import logger
import json
import threading


def get_or_none(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None


def _worker():
    while True:
        func, args, kwargs = _queue.get()
        try:
            func(*args, **kwargs)
        except:
            import traceback
            details = traceback.format_exc()
            logger.error(__name__, details)
        finally:
            _queue.task_done()  # so we can join at exit


def postpone(func):
    def decorator(*args, **kwargs):
        _queue.put((func, args, kwargs))
    return decorator

_queue = queue.Queue()
_thread = threading.Thread(target=_worker)
_thread.daemon = True
_thread.start()


def _cleanup():
    _queue.join()   # so we don't exit too soon

atexit.register(_cleanup)


def read_data(filename):
    try:
        with open('agents_platform/storage/' + filename) as f:
            # dic = json.load(f)
            return json.load(f)
    except Exception as e:
        logger.error(__name__, e)
        return {}


def write_data(filename, data):
    try:
        with open('agents_platform/storage/' + filename, 'w', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False))
            f.flush()
    except Exception as e:
        logger.error(__name__, e)
