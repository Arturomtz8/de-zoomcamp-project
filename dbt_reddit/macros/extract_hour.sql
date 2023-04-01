{#
    This macro extracts the hour of the timestamp
#}
{% macro extract_hour(column_name) -%}

format_timestamp('%H', {{ column_name }})

{%- endmacro %}
