import dateutil.parser
from datetime import datetime, timedelta

from django.db import IntegrityError

from .models import Call, CallBills, Charges


class ApiService:
    def __init__(self, params):
        self.call_id = params.get('call_id')
        self.start = params.get('start')
        self.stop = params.get('stop')

    def process_calls(self):
        try:
            start_record = dateutil.parser.parse(self.start['record_timestamp'])
            record_start = self.start['record_timestamp']
            record_stop = self.stop['record_timestamp']

            call = {
                'id': self.call_id,
                'source': self.start['source'],
                'destination': self.start['destination'],
                'record_start': record_start,
                'record_stop': record_stop

            }
            call = Call(**call)
            call.save()

            price, days_diff = self.calculate_bills(record_start, record_stop)
            duration = self.calculate_duration(days_diff)

            bill = {
                'price': price,
                'call_start_date': start_record.date(),
                'call_start_time': start_record.time(),
                'duration': duration,
                'call': call

            }
            bill = CallBills(**bill)
            bill.save()
        except IntegrityError as e:
            raise IntegrityError(e.args[0])
        except KeyError as key:
            raise KeyError(key.args[0])
        except Exception as ex:
            raise Exception(ex.args[0])

    @staticmethod
    def calculate_duration(days_diff):
        hours, remainder = divmod(days_diff.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        return '{}:{}:{}'.format(int(hours), int(minutes), int(seconds))

    def calculate_bills(self, start_record, stop_record):
        try:
            charge = ChargeService.get_charge().first()
            start_record = dateutil.parser.parse(start_record)
            stop_record = dateutil.parser.parse(stop_record)
            days_diff = stop_record - start_record

            if days_diff.days != 0:
                start_record += timedelta(days=days_diff.days)
                start_date, stop_date = self.set_time(start_record, stop_record)

                minutes_day = (days_diff.days * charge.useful_day) * 60
                minutes_remaining = (stop_date - start_date).total_seconds() / 60
                minutes = minutes_day + minutes_remaining
                price = (minutes * charge.call_charge) + charge.standing_charge
            else:
                start_date, stop_date = self.set_time(start_record, stop_record)
                minutes = (stop_date - start_date).total_seconds() / 60
                price = (minutes * charge.call_charge) + charge.standing_charge

            return round(price, 2), days_diff

        except Exception as e:
            raise Exception('Calculate bills erro - ' + e.args[0])

    def set_time(self, start_record, stop_record):
        start_date = self.set_start_time(start_record)
        stop_date = self.set_stop_time(stop_record)
        return start_date, stop_date

    @staticmethod
    def set_start_time(start_record):
        if start_record.hour < 6:
            start_date = datetime.strptime(str(start_record), '%Y-%m-%d %H:%M:%S+00:00')\
                .replace(hour=6, minute=00, second=00)
        elif start_record.hour > 22:
            start_date = datetime.strptime(str(start_record), '%Y-%m-%d %H:%M:%S+00:00')\
                .replace(hour=22, minute=00, second=00)
        else:
            start_date = datetime.strptime(str(start_record), '%Y-%m-%d %H:%M:%S+00:00')
        return start_date

    @staticmethod
    def set_stop_time(stop_record):
        if stop_record.hour < 6:
            stop_date = datetime.strptime(str(stop_record), '%Y-%m-%d %H:%M:%S+00:00')\
                .replace(hour=6, minute=00, second=00)
        elif stop_record.hour > 22:
            stop_date = datetime.strptime(str(stop_record), '%Y-%m-%d %H:%M:%S+00:00')\
                .replace(hour=22, minute=00, second=00)
        else:
            stop_date = datetime.strptime(str(stop_record), '%Y-%m-%d %H:%M:%S+00:00')
        return stop_date

    @staticmethod
    def get_call(id):
        call = Call.objects.filter(id=id).select_related('callbills')
        return call


class ChargeService:
    def __init__(self, params):
        self.standing_charge = params.get('standing_charge')
        self.call_charge = params.get('call_charge')
        self.useful_day = params.get('useful_day')

    def save_charge(self):
        if self.get_charge():
            self._update_charge()
        self._save()

    def _save(self):
        try:
            charges = {
                'standing_charge': float(self.standing_charge),
                'call_charge': float(self.call_charge),
                'useful_day': int(self.useful_day),
                'status': 1,
                'create_date': datetime.now()
            }
            charges = Charges(**charges)
            charges.save()
        except IntegrityError as e:
            raise IntegrityError(e.args[0])
        except Exception as ex:
            raise Exception(ex.args[0])

    @staticmethod
    def get_charge():
        return Charges.objects.filter(status=1)

    @staticmethod
    def _update_charge():
        return Charges.objects.filter(status=1).update(status=0)
