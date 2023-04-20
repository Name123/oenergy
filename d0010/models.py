from django.db import models


class DataFile(models.Model):
    filename = models.TextField()
    loaded_at = models.DateTimeField(auto_now=True)
  

class MpanData(models.Model):
    mpan_core = models.IntegerField(unique=True)
    validation_status = models.CharField(max_length=1)


class MeterData(models.Model):
    meter_serial_num = models.CharField(max_length=10, unique=True)
    reading_type = models.CharField(max_length=1)


class RegisterReading(models.Model):
    data_file = models.ForeignKey(DataFile, on_delete=models.CASCADE)
    mpan = models.ForeignKey(MpanData, on_delete=models.CASCADE)
    meter = models.ForeignKey(MeterData, on_delete=models.CASCADE)
    meter_register_id = models.CharField(max_length=2)
    datetime = models.DateTimeField()
    value = models.FloatField()
    method = models.CharField(max_length=1)

    class Meta:
        unique_together = ('datetime', 'mpan', 'meter', 'meter_register_id')
