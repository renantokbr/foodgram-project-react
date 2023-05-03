from rest_framework.serializers import ValidationError


def class_obj_validate(value: str, form: object = None) -> object:
    if not str(value).isdecimal():
        raise ValidationError(f'В строке {value} должно быть число.')
    if form:
        obj = form.objects.filter(id=value)
        if not obj:
            raise ValidationError(f'Объект {type(form)} '
                                  f'с ID={value} не существует.')
        return obj[0]
    return None
