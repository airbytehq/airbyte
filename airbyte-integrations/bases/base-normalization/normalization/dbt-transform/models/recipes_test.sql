SELECT
    *
FROM
    {{ SOURCE(
        'data',
        'recipes_json'
    ) }}