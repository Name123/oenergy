import os
import typing as t
from datetime import datetime
from enum import Enum

from django.db import transaction


from d0010.models import DataFile, MpanData, MeterData, RegisterReading


class MessageType(str, Enum):
    Header = 'ZHV'
    Footer = 'ZPT'
    MpanData = '026'
    MeterData = '028'
    RegisterReading = '030'


def parse_timestamp(s: str) -> datetime:
    return datetime.strptime(s, '%Y%m%d%H%M%S')


class FlowD0010Parser:
    DELIMITER = '|'


    def __init__(self) -> None:
        self._init_new_file()


    def _init_new_file(self) -> None:
        self._line_num = 0
        self._curr_file = None
        self._curr_mpan = None
        self._curr_meter_info = None
        self._curr_readings = []

        self._is_header_read = False
        self._is_footer_read = False


    def _assert_consistency(self) -> None:
        assert self._is_header_read, 'Data before header'
        assert not self._is_footer_read, 'Data after footer'


    def _parse_header(self, rest_vals: t.List) -> None:
        # TODO: extract relevant data from header
        assert self._line_num == 0, 'Header out of place'
        self._is_header_read = True


    def _parse_footer(self, rest_vals: t.List) -> None:
        # TODO: extract relevant data from footer
        self._is_footer_read = True
        self._flush_buffer()


    def _parse_mpan_data(self, rest_vals: t.List) -> None:
        self._assert_consistency()
        self._flush_buffer()
        mpan_core, validation_status = rest_vals
        self._curr_mpan, _ = MpanData.objects.update_or_create(
            mpan_core=mpan_core,
            defaults={
                'validation_status': validation_status,
            }
        )


    def _parse_meter_data(self, rest_vals: t.List) -> None:
        self._assert_consistency()
        serial_num, reading_type = rest_vals
        self._curr_meter_info, _ = MeterData.objects.update_or_create(
            meter_serial_num=serial_num,
            defaults={
                'reading_type': reading_type,
            }
        )



    def _parse_reading(self, rest_vals: t.List) -> None:
        self._assert_consistency()
        assert self._curr_mpan is not None
        assert self._curr_file is not None
        assert self._curr_meter_info is not None
        register_id, timestamp, reading, _, _, _, reading_method = rest_vals
        self._curr_readings.append(
            RegisterReading(
                mpan=self._curr_mpan,
                data_file=self._curr_file,
                meter=self._curr_meter_info,
                datetime=parse_timestamp(timestamp),
                value=reading,
                meter_register_id=register_id,
                method=reading_method,
            )
        )


    def _flush_buffer(self) -> None:
        RegisterReading.objects.bulk_create(self._curr_readings)
        self._curr_mpan = None
        self._curr_meter_info = None
        self._curr_readings = []


    def _parse_line(self, line: str) -> None:
        vals = line.split(self.DELIMITER)
        vals = vals[:-1]  # line always ends with a delimiter

        msg_type, rest_vals = vals[0], vals[1:]
        if msg_type == MessageType.Header:
            self._parse_header(rest_vals)
        elif msg_type == MessageType.Footer:
            self._parse_footer(rest_vals)
        elif msg_type == MessageType.MpanData:
            self._parse_mpan_data(rest_vals)
        elif msg_type == MessageType.MeterData:
            self._parse_meter_data(rest_vals)
        elif msg_type == MessageType.RegisterReading:
            self._parse_reading(rest_vals)
        else:
            raise NotImplementedError(f'Unknown message {msg_type}')

        self._line_num += 1

    def run(self, filename: str) -> None:
        self._init_new_file()
        with open(filename, 'r') as f:
            with transaction.atomic():

                self._curr_file = DataFile(filename=os.path.basename(filename))
                self._curr_file.save()

                for line in f:
                    self._parse_line(line.rstrip('\n'))

            assert self._is_footer_read, 'Footer is not read'
