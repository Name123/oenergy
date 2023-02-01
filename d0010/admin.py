from django.contrib import admin
from d0010.models import DataFile, RegisterReading


class RegisterReadingAdmin(admin.ModelAdmin):
    model = RegisterReading
    list_display = ('datetime', 'value', 'meter_register_id', 'filename', 'mpan_core', 'meter_serial_num')
    list_filter = ('mpan__mpan_core', 'meter__meter_serial_num')

    def filename(self, obj):
        return obj.data_file.filename

    def mpan_core(self, obj):
        return obj.mpan.mpan_core

    def meter_serial_num(self, obj):
        return obj.meter.meter_serial_num


class DataFileAdmin(admin.ModelAdmin):
    model = DataFile
    list_display = ('filename', 'loaded_at')


admin.site.register(RegisterReading, RegisterReadingAdmin)
admin.site.register(DataFile, DataFileAdmin)
