from sattogo.middleware import BaseSerializer
from .models import Event, EventSession, Attendance

from rest_framework import serializers

class EventSessionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventSession
        fields = ['pk','title', 'deadline']  # Specify desired fields


class ConfirmEventSerialiazer(serializers.Serializer):
    pk = serializers.CharField(max_length=100)
    magic_string = serializers.CharField(max_length=300)

    def validate(self, data):
        """
        Custom validation to ensure both 'pk' and 'magic_string' are present.

        Raises a ValidationError if either field is missing.
        """

        required_fields = ['pk', 'magic_string']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            raise serializers.ValidationError({
                'detail': f"Missing required fields: {', '.join(missing_fields)}"
            })

        return data

    def user_is_allowed(self,data):
        magic_string = self.context.get('magic_string')
        pk = self.context.get('pk')
        matching_event_session = EventSession.objects.select_related('parent_event').prefetch_related('attendance_set').get(pk=pk)
        parent_event = matching_event_session.parent_event


        if parent_event.is_public != True:
            attendance  =  matching_event_session.attendance_set.all().get(magic_string=magic_string)
            if not attendance:
                raise serializers.ValidationError(detail='You are not verified to attend this event',code=401)
        return data

    class Meta:
        model = EventSession
        fields = ['pk','magic_string']  # Specify desired fields

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['first_name','last_name','user','event']


class EventReadSerializer(serializers.ModelSerializer):
    sessions = EventSessionReadSerializer(source='eventsession_set', many=True)
    class Meta:
        model = Event
        fields = ('name', 'deadline', 'event_type', 'venue', 'reward', 'sessions')


class EventSerializer(BaseSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        validators = [
            BaseSerializer.validate_required
        ]

