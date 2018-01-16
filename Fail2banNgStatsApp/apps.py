import sys

from django.apps import AppConfig
from django.conf import settings

from .statsutils import get_logger

class Fail2banNgStatsAppConfig(AppConfig):
    name = 'Fail2banNgStatsApp'

    def ready(self):
        if settings.REFRESH_ON or not self.__server_starting():
            return

        self.logger = get_logger('Fail2banNgStatsAppConfig')
        lock = settings.REFRESH_LOCK
        if lock.acquire(blocking=False):
            settings.REFRESH_ON = True
            try:
                self.logger.info('Run scheduled refresh')
                self.__run_scheduled_refresh()
            except Exception as e:
                self.logger.warning('Failed to run shceduled refresh')
                self.logger.debug(str(e))
            lock.release()

    def __server_starting(self):
        if len(sys.argv) >= 2:
            return sys.argv[1] == 'runserver'
        return False

    def __refresh_thread_job(self, exit_event):
        from .statsreader import read_config, run_scheduled_refresh
        from .statsutils import ArgsMock
        args = ArgsMock(config_path=settings.REFRESH_CONFIG, database=True)
        _config = dict(read_config(args.config))
        _config['event'] = exit_event
        self.logger.debug(str(_config))
        run_scheduled_refresh(args, _config)

    def __run_scheduled_refresh(self):
        from threading import Event, Thread
        import atexit

        exit_event = Event()
        thread = Thread(target=self.__refresh_thread_job, args=(exit_event,), daemon=True)
        thread.start()

        atexit.register(self.__join_refresh_thread, thread, exit_event)

    def __join_refresh_thread(self, thread, exit_event):
        exit_event.set()
        self.logger.debug('Join refresh thread')
        thread.join(timeout=float(15))
        if thread.is_alive():
            self.logger.warning('Refreash thread join timed out.')
        else:
            self.logger.info('Refresh thread terminated')
