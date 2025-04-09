# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
import numbers # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args
try:
    from dash.development.base_component import ComponentType # noqa: F401
except ImportError:
    ComponentType = typing.TypeVar("ComponentType", bound=Component)


class DangerouslySetInnerHtml(Component):
    """A DangerouslySetInnerHtml component.
ExampleComponent is an example component.
It renders an input with the property `value`
which is editable by the user.

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- value (string; optional):
    The html content of the div."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dangerously_set_inner_html'
    _type = 'DangerouslySetInnerHtml'

    @_explicitize_args
    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        value: typing.Optional[str] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'value']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'value']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DangerouslySetInnerHtml, self).__init__(**args)
