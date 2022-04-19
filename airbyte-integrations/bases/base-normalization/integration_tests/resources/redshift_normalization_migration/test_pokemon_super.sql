select forms from {{ ref('pokemon' )}} where forms != json_parse('[{"name":"ditto","url":"https://pokeapi.co/api/v2/pokemon-form/132/"}]')
