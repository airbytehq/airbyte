SELECT
    forms
FROM
    {{ REF('pokemon') }}
WHERE
    forms != json_parse('[{"name":"ditto","url":"https://pokeapi.co/api/v2/pokemon-form/132/"}]')