# AUTO GENERATED FILE - DO NOT EDIT

export dangerouslysetinnerhtml

"""
    dangerouslysetinnerhtml(;kwargs...)

A DangerouslySetInnerHtml component.
ExampleComponent is an example component.
It renders an input with the property `value`
which is editable by the user.
Keyword arguments:
- `id` (String; optional): The ID used to identify this component in Dash callbacks.
- `value` (String; optional): The html content of the div.
"""
function dangerouslysetinnerhtml(; kwargs...)
        available_props = Symbol[:id, :value]
        wild_props = Symbol[]
        return Component("dangerouslysetinnerhtml", "DangerouslySetInnerHtml", "dangerously_set_inner_html", available_props, wild_props; kwargs...)
end

