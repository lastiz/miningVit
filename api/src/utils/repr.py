from six import string_types


class ReprMixin:
    __abstract__ = True

    __repr_attrs__ = []
    __repr_max_length__ = 25

    @property
    def _repr_attrs_str(self):
        max_length = self.__repr_max_length__

        values = []
        single = len(self.__repr_attrs__) == 1
        for key in self.__repr_attrs__:
            if not hasattr(self, key):
                raise KeyError(
                    "{} has incorrect attribute '{}' in "
                    "__repr__attrs__".format(self.__class__, key)
                )
            value = getattr(self, key)
            wrap_in_quote = isinstance(value, string_types)

            value = str(value)
            if len(value) > max_length:
                value = value[:max_length] + "..."

            if wrap_in_quote:
                value = "'{}'".format(value)
            values.append(value if single else "{}:{}".format(key, value))

        return " ".join(values)

    def __repr__(self):
        # join class name, id and repr_attrs
        return "<{}{}>".format(
            self.__class__.__name__,
            " " + self._repr_attrs_str if self._repr_attrs_str else "",
        )
