from datetime import datetime


from django.test import TestCase


from d0010.models import DataFile, MeterData, MpanData, RegisterReading
from d0010.parse import FlowD0010Parser


class ParserTest(TestCase):
    def setUp(self):
        self._parser = FlowD0010Parser()
        self._parser._curr_file = DataFile(filename='test.txt')
        self._parser._curr_file.save()

    def test_header_parsing(self) -> None:
        self.assertFalse(self._parser._is_header_read)
        self._parser._parse_line('ZHV|')
        self.assertTrue(self._parser._is_header_read)

    def test_footer_parsing(self) -> None:
        self.assertFalse(self._parser._is_footer_read)
        self._parser._parse_line('ZPT|')
        self.assertTrue(self._parser._is_footer_read)

    def test_mpan_parsing(self) -> None:
        self.assertIsNone(self._parser._curr_mpan)
        self._parser._parse_line('ZHV|')
        self.assertEqual(MpanData.objects.count(), 0)
        self._parser._parse_line('026|12345|V|')
        self.assertEqual(MpanData.objects.count(), 1)
        obj = MpanData.objects.first()
        self.assertEqual(obj.mpan_core, 12345)
        self.assertEqual(obj.validation_status, 'V')
        

    def test_reading_parsing(self) -> None:
        self._parser._parse_line('ZHV|')
        self._parser._parse_line('026|12345|V|')
        self._parser._parse_line('028|ABC 00|D|')
        self._parser._parse_line('030|01|20220101000000|100.0||||N|')
        self._parser._parse_line('ZPT|')
        mpan = MpanData.objects.first()
        meter = MeterData.objects.first()
        reading = RegisterReading.objects.first()
        self.assertEqual(reading.mpan, mpan)
        self.assertEqual(reading.meter, meter)
        self.assertEqual(int(reading.value), 100)
        self.assertEqual(reading.meter_register_id, '01')
