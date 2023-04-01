{#
    This macro converts minutes and seconds to 0
#}
{% macro normalize_timestamp(column_value) -%}

format_datetime('%Y-%m-%d %H:00:00', datetime_trunc({{ column_value }}, hour))

{%- endmacro %}
