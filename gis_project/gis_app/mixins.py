
class HaystackUrlSerializerMixin:
    def get_url(self, obj):
        return obj.object.get_absolute_url()
